# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.abc
import importlib.machinery
import importlib.metadata
import os.path
import pathlib
import sqlite3
import sys
import types
import typing

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
            loader=SqliteLoader(source),
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
    def __init__(self, source: str) -> None:
        self.source = source

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> None:
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        exec(self.source, module.__dict__)


def load(database: pathlib.Path | str | sqlite3.Connection) -> None:
    if isinstance(database, (pathlib.Path, str)):
        if not os.path.isfile(database):
            raise FileNotFoundError(f"{database} must exist.")
        database = pathlib.Path(database)
    sys.meta_path.append(SqliteFinder(database))


class SqliteDistribution(importlib.metadata.Distribution):
    def __init__(self, name: str, connection: sqlite3.Connection):
        self.__name = name
        self.__connection = connection
        self.__accessor = Accessor(connection)

    def locate_file(self, path: typing.Any) -> pathlib.Path:
        raise NotImplementedError()

    def read_text(self, filename: str) -> str:
        return self.__accessor.get_file(f"{self.__name}-%/{filename}")
