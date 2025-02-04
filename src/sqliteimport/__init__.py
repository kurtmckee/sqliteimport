# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import sys

from .importer import load

__all__ = ("load",)


# Load `.sqlite3` files on the Python path.
for path in sys.path:
    if path.endswith(".sqlite3"):
        try:
            load(path)
        except FileNotFoundError:
            pass
