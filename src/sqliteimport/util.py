# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import importlib.util
import sys


def get_magic_number() -> int:
    return int.from_bytes(importlib.util.MAGIC_NUMBER[:2], "little")


def get_python_identifier() -> str:
    known_names = {
        "cpython": "CPython",
        "pypy": "PyPy",
    }
    name = known_names.get(sys.implementation.name) or sys.implementation.name
    version = ".".join(str(v) for v in sys.version_info[:3])
    if sys.version_info[3] != "final":
        version += "".join(str(v) for v in sys.version_info[3:])

    identifier = f"{name} {version}"

    if sys.implementation.name == "pypy":
        pypy_version = ".".join(str(v) for v in sys.implementation.version[:3])
        if sys.implementation.version[3] != "final":
            pypy_version += "".join(str(v) for v in sys.implementation.version[3:])
        identifier += f" [{pypy_version}]"

    return identifier
