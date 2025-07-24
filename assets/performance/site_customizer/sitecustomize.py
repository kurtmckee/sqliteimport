# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import sys

# Immediately remove the current directory from PYTHONPATH.
sys.path = [path for path in sys.path if not (path and __file__.startswith(path))]

import sqliteimport  # noqa: F401,E402
