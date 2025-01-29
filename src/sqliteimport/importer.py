# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.abc
import importlib.machinery
import importlib.metadata
import io
import os.path
import pathlib
import sqlite3
import sys
import types
import typing

if sys.version_info >= (3, 11):
    from importlib.resources.abc import Traversable, TraversableResources
else:
    from importlib.abc import Traversable, TraversableResources

from sqliteimport.accessor import Accessor


class SqliteFinder(importlib.abc.MetaPathFinder):
    def __init__(self, database: pathlib.Path | sqlite3.Connection) -> None:
        if isinstance(database, pathlib.Path):
            self.database = database
            self.connection = sqlite3.connect(database)
        else:  # isinstance(database, sqlite3.Connection)
            _, _, path = database.execute("PRAGMA database_list;").fetchone()
            self.database = pathlib.Path(path)
            self.connection = database
        self.accessor = Accessor(self.connection)

    def find_spec(
        self,
        fullname: str,
        path: typing.Sequence[str] | None,
        target: types.ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        query = "SELECT source, is_package FROM code WHERE fullname = ?;"
        result = self.connection.execute(query, (fullname,)).fetchone()
        if result is None:
            return None

        source, is_package = result
        spec = importlib.machinery.ModuleSpec(
            name=fullname,
            loader=SqliteLoader(source, self.accessor),
            origin=self.database.name,
            is_package=is_package,
        )
        return spec

    def find_distributions(
        self,
        context: importlib.metadata.DistributionFinder.Context | None = None,
    ) -> typing.Generator[SqliteDistribution]:
        if context is None:
            context = importlib.metadata.DistributionFinder.Context()
        if context.name is not None:
            yield SqliteDistribution(context.name, self.connection)


class SqliteLoader(importlib.abc.Loader):
    def __init__(self, source: str, accessor: Accessor) -> None:
        self.source = source
        self.accessor = accessor

    def exec_module(self, module: types.ModuleType) -> None:
        exec(self.source, module.__dict__)

    def get_resource_reader(self, fullname: str) -> SqliteTraversableResources:
        return SqliteTraversableResources(fullname, self.accessor)


def load(database: pathlib.Path | str | sqlite3.Connection) -> None:
    if isinstance(database, (pathlib.Path, str)):
        if not os.path.isfile(database):
            raise FileNotFoundError(f"{database} must exist.")
        database = pathlib.Path(database)
    sys.meta_path.append(SqliteFinder(database))


class SqliteDistribution(importlib.metadata.Distribution):
    def __init__(self, name: str, connection: sqlite3.Connection) -> None:
        self.__name = name
        self.__connection = connection
        self.__accessor = Accessor(connection)

    def locate_file(self, path: typing.Any) -> pathlib.Path:
        raise NotImplementedError()

    def read_text(self, filename: str) -> str:
        return self.__accessor.get_file(f"{self.__name}-%/{filename}").decode("utf-8")


class SqliteTraversableResources(TraversableResources):
    def __init__(self, fullname: str, accessor: Accessor) -> None:
        self.fullname = fullname
        self.accessor = accessor

    def files(self) -> SqliteTraversable:
        return SqliteTraversable(self.fullname, self.accessor)


class SqliteTraversable(Traversable):
    def __init__(self, path: str, accessor: Accessor) -> None:
        self._path = path
        self._accessor = accessor

    def iterdir(self) -> typing.Iterator[SqliteTraversable]:
        for path in self._accessor.list_directory(self._path):
            yield SqliteTraversable(path, self._accessor)

    def joinpath(self, *descendants: str) -> SqliteTraversable:
        return SqliteTraversable(
            f"{self._path}/{'/'.join(descendants)}", self._accessor
        )

    def __truediv__(self, other: str) -> SqliteTraversable:
        return self.joinpath(other)

    def is_dir(self) -> bool:
        return False

    def is_file(self) -> bool:
        return True

    @typing.overload
    def open(
        self,
        mode: typing.Literal["r"] = ...,
        encoding: str | None = ...,
        errors: str | None = ...,
    ) -> io.StringIO: ...

    @typing.overload
    def open(
        self,
        mode: typing.Literal["rb"] = ...,
        encoding: str | None = ...,
        errors: str | None = ...,
    ) -> io.BytesIO: ...

    def open(
        self,
        mode: str = "r",
        encoding: str | None = None,
        errors: str | None = None,
        *_: typing.Any,
        **__: typing.Any,
    ) -> io.StringIO | io.BytesIO:
        encoding = encoding if encoding is not None else "utf-8"
        errors = errors if errors is not None else "strict"
        content = self._accessor.get_file(self._path)
        if "b" in mode:
            return io.BytesIO(content)

        return io.StringIO(content.decode(encoding, errors=errors))

    def read_text(self, encoding: str | None = None, errors: str | None = None) -> str:
        encoding = encoding if encoding is not None else "utf-8"
        errors = errors if errors is not None else "strict"
        return self._accessor.get_file(self._path).decode(encoding, errors)

    def read_bytes(self) -> bytes:
        return self._accessor.get_file(self._path)

    @property
    def name(self) -> str:
        return pathlib.PurePosixPath(self._path).name


# noinspection PyUnresolvedReferences,PyProtectedMember
def _patch_python_39_from_package() -> None:
    # Python 3.9's `from_package()` implementation simply returns a `pathlib.Path`,
    # so the function must be patched to support sqlite-backed resource access.
    import functools
    import importlib._common  # type: ignore[import-not-found]

    original_from_package: typing.Callable[[types.ModuleType], Traversable] = (
        importlib._common.from_package
    )

    @functools.wraps(original_from_package)
    def _from_package(package: types.ModuleType) -> Traversable:
        spec = package.__spec__
        if spec is None:
            return original_from_package(package)

        loader = spec.loader
        if not isinstance(loader, SqliteLoader):
            return original_from_package(package)
        return loader.get_resource_reader(spec.name).files()

    importlib._common.from_package = _from_package


if sys.version_info < (3, 10):
    _patch_python_39_from_package()
