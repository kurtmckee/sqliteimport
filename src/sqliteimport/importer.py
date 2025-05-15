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
import tokenize
import types
import typing

from .accessor import Accessor
from .compat import (
    Traversable,
    TraversableResources,
    accommodate_python_39_from_package_behavior,
)


class SqliteFinder(importlib.metadata.DistributionFinder):
    def __init__(self, database: pathlib.Path | sqlite3.Connection) -> None:
        if isinstance(database, pathlib.Path):
            self.database = database
            self.connection = sqlite3.connect(database)
        else:  # isinstance(database, sqlite3.Connection)
            self.database = pathlib.Path(Accessor.get_database_path(database))
            self.connection = database
        self.accessor = Accessor(self.connection)

    def find_spec(
        self,
        fullname: str,
        path: typing.Sequence[str] | None,
        target: types.ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        result = self.accessor.find_spec(fullname)
        if result is None:
            return None

        path, source, is_package = result
        if isinstance(source, types.CodeType):
            code = source
        else:  # isinstance(source, bytes)
            code = compile(source, filename=path, mode="exec", dont_inherit=True)
        spec = importlib.machinery.ModuleSpec(
            name=fullname,
            loader=SqliteLoader(code, self.accessor),
            origin=self.database.name,
            is_package=is_package,
        )
        spec.has_location = True
        if isinstance(source, types.CodeType):
            spec.cached = self.database.name
        else:
            spec.cached = None

        return spec

    def find_distributions(
        self,
        context: importlib.metadata.DistributionFinder.Context | None = None,
    ) -> typing.Generator[SqliteDistribution]:
        if context is None:
            context = importlib.metadata.DistributionFinder.Context()

        for module in self.accessor.find_distributions(context.name):
            yield SqliteDistribution(module, self.connection)


@accommodate_python_39_from_package_behavior
class SqliteLoader(importlib.abc.InspectLoader):
    def __init__(self, code: types.CodeType, accessor: Accessor) -> None:
        self.code = code
        self.accessor = accessor

    def exec_module(self, module: types.ModuleType) -> None:
        exec(self.code, module.__dict__)

    def get_resource_reader(self, fullname: str) -> SqliteTraversableResources:
        return SqliteTraversableResources(fullname, self.accessor)

    def get_source(self, fullname: str) -> str:
        raw_content = self.accessor.get_file(fullname=fullname)
        encoding, _ = tokenize.detect_encoding(io.BytesIO(raw_content).readline)
        return raw_content.decode(encoding)


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

    if sys.version_info < (3, 10):
        # The `.name` property doesn't exist in Python 3.9.
        @property
        def name(self) -> str:
            return self.metadata["Name"]

    def locate_file(self, path: typing.Any) -> pathlib.Path:
        raise NotImplementedError()

    def read_text(self, filename: str) -> str:
        raw_content = self.__accessor.get_file(path=f"{self.__name}-%/{filename}")
        return raw_content.decode("utf-8")


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
        content = self._accessor.get_file(path=self._path)
        if "b" in mode:
            return io.BytesIO(content)

        return io.StringIO(content.decode(encoding, errors=errors))

    def read_text(self, encoding: str | None = None, errors: str | None = None) -> str:
        encoding = encoding if encoding is not None else "utf-8"
        errors = errors if errors is not None else "strict"
        return self._accessor.get_file(path=self._path).decode(encoding, errors)

    def read_bytes(self) -> bytes:
        return self._accessor.get_file(path=self._path)

    @property
    def name(self) -> str:
        return pathlib.PurePosixPath(self._path).name
