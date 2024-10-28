# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pathlib
import sqlite3


class Accessor:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def initialize_database(self) -> None:
        """Create database tables and insert basic information about the database."""

        self.connection.executescript(
            """
            CREATE TABLE sqliteimport (
                field TEXT,
                value TEXT
            );

            INSERT INTO sqliteimport (field, value)
            VALUES
                ('version', 'beta'),
                ('creation_date', strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            ;

            CREATE TABLE code (
                fullname text,
                path text,
                is_package boolean,
                source text
            );

            CREATE INDEX fullname_index ON code (fullname);
            """
        )

    def add_file(self, directory: pathlib.Path, file: pathlib.Path) -> None:
        """Add a file to the database."""

        fullname = ""
        is_package = False

        if file.name == "__init__.py":
            is_package = True
            fullname = str(file.parent)
        elif file.suffix == ".py":
            fullname = str(file.with_suffix(""))

        self.connection.execute(
            """
            INSERT INTO code (fullname, path, is_package, source)
            VALUES (?, ?, ?, ?);
            """,
            (
                fullname.replace("/", ".").replace("\\", "."),
                str(file),
                is_package,
                (directory / file).read_text(),
            ),
        )
