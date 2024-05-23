# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.abc
import importlib.machinery
import os.path
import pathlib
import sqlite3
import sys
import types
import typing


class SqliteFinder(importlib.abc.MetaPathFinder):
    def __init__(self, database: pathlib.Path | sqlite3.Connection) -> None:
        if isinstance(database, pathlib.Path):
            self.database = database
            self.connection = sqlite3.connect(database)
        else:  # isinstance(database, sqlite3.Connection)
            _, _, path = database.execute("PRAGMA database_list;").fetchone()
            self.database = pathlib.Path(path)
            self.connection = database

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
