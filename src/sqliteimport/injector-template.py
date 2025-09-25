# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
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


if sys.version_info < (3, 11):
    msg = """
        Python 3.11 or higher is required to run this program.
        (Python {sys.version} detected.)
        ----
        If you are a user:
        This program may support Python 3.10 and lower in other circumstances.
        However, it is packaged in a way that requires Python 3.11 and higher.
        If you have access to Python 3.11 or higher,
        you may be able to re-run the program.
        ----
        If you are developer:
        This program's Python dependencies were injected using sqliteimport.
        Only Python 3.11 and higher have compatible sqlite3 APIs to support this.
    """
    raise RuntimeError(msg)


class DictFinder(importlib.metadata.DistributionFinder):
    def __init__(self, modules: dict[str, str]) -> None:
        self.modules = modules

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
