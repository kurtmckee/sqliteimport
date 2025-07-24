# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import enum
import pathlib

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
PACKAGE_DIRECTORY = REPO_ROOT / "build/perftest"
STATS = REPO_ROOT / "build/perfstats"


class Importer(enum.StrEnum):
    filesystem = "filesystem"
    zipimport = "zipimport"
    sqliteimport = "sqliteimport"


class CodeType(enum.StrEnum):
    source = "source"
    bytecode = "bytecode"


class Measurement(enum.StrEnum):
    time = "time"
    size = "size"


PACKAGE_PATHS: dict[Importer, dict[CodeType, pathlib.Path]] = {
    Importer.filesystem: {
        CodeType.source: PACKAGE_DIRECTORY,
        CodeType.bytecode: PACKAGE_DIRECTORY,
    },
    Importer.zipimport: {
        CodeType.source: STATS / "source.zip",
        CodeType.bytecode: STATS / "bytecode.zip",
    },
    Importer.sqliteimport: {
        CodeType.source: STATS / "source.sqlite3",
        CodeType.bytecode: STATS / "bytecode.sqlite3",
    },
}

LOG_PATHS: dict[Importer, dict[CodeType, pathlib.Path]] = {
    # This is a dictionary comprehension.
    importer: {
        code_type: STATS / f"{importer}.{code_type}.log" for code_type in CodeType
    }
    for importer in Importer
}
