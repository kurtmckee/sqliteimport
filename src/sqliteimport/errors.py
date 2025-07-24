# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT


class SqliteImportError(Exception):
    pass


class FileNotFoundInDatabaseError(SqliteImportError, FileNotFoundError):
    def __init__(self, filename: str, database_path: str) -> None:
        super().__init__(
            2, "File not found in database", filename, None, database_path or ":memory:"
        )
