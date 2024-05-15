# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.abc
import importlib.machinery
import pathlib
import sqlite3
import sys
import types
import typing


class SqliteFinder(importlib.abc.MetaPathFinder):
    def __init__(self, database: pathlib.Path) -> None:
        self.database = database
        self.connection = sqlite3.connect(database)

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


def load(database: pathlib.Path | str) -> None:
    sys.meta_path.append(SqliteFinder(pathlib.Path(database)))
