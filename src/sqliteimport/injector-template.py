# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2026 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import importlib.machinery
import importlib.metadata
import sqlite3
import sys
import types
import typing

# IGNORE: START
# -------------
# The lines here allow coherent type-checking of this file.
# However, the actual lines are removed and replaced when this template is rendered.
database: bytes = b""
sqliteimport_modules: dict[str, str] = {}  # Inject: sqliteimport_modules
# -------------
# IGNORE: END


class DictFinder(importlib.metadata.DistributionFinder):
    def __init__(self, modules: dict[str, str]) -> None:
        self.modules = modules

    # pyrefly: ignore [missing-override-decorator]
    def find_spec(
        self,
        fullname: str,
        path: typing.Sequence[str] | None,
        target: types.ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        if not (fullname == "sqliteimport" or fullname.startswith("sqliteimport.")):
            return None
        if fullname not in self.modules:
            return None

        if fullname == "sqliteimport":
            path = "sqliteimport/__init__.py"
            is_package = True
        else:
            path = fullname.replace(".", "/") + ".py"
            is_package = False
        source = self.modules[fullname]
        code = compile(source, filename=path, mode="exec", dont_inherit=True)
        spec = importlib.machinery.ModuleSpec(
            name=fullname,
            loader=DictLoader(code, source),
            origin=f"dict://{path}",
            is_package=is_package,
        )
        spec.has_location = False
        spec.cached = None

        return spec

    def find_distributions(
        self,
        context: importlib.metadata.DistributionFinder.Context | None = None,
    ) -> typing.Iterable[importlib.metadata.Distribution]:
        yield from ()


class DictLoader(importlib.abc.InspectLoader):
    def __init__(self, code: types.CodeType, source: str) -> None:
        self.code = code
        self.source = source

    # pyrefly: ignore [missing-override-decorator]
    def exec_module(self, module: types.ModuleType) -> None:
        exec(self.code, module.__dict__)

    def get_source(self, fullname: str) -> str:
        return self.source


# Import sqliteimport.
sys.meta_path.insert(0, DictFinder(sqliteimport_modules))
import sqliteimport  # noqa: E402

del sys.meta_path[0]

# Load the database in-memory.
connection = sqlite3.connect(":memory:")
connection.deserialize(database)
sqliteimport.load(connection)
