# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import typing


class SqliteImportError(Exception):
    pass


class FileNotFoundInDatabaseError(SqliteImportError, FileNotFoundError):
    @typing.overload
    def __init__(self, filename: str, database_path: str, /) -> None: ...

    @typing.overload
    def __init__(
        self,
        errno: int,
        strerror: str,
        filename: str,
        characters_written: None,
        database_path: str,
        /,
    ) -> None: ...

    def __init__(self, *args: int | str | None) -> None:
        if len(args) == 2:
            args = (
                2,
                "File not found in database",
                args[0],
                None,
                args[1] or ":memory:",
            )
        super().__init__(*args)
