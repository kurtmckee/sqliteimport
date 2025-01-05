# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
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
                str(pathlib.PurePosixPath(file)),
                is_package,
                (directory / file).read_bytes(),
            ),
        )

    def get_file(self, path_like: str) -> bytes:
        source: bytes = self.connection.execute(
            """
            SELECT
                source
            FROM code
            WHERE path LIKE ?;
            """,
            (path_like,),
        ).fetchone()[0]
        return source

    def list_directory(self, path_like: str) -> list[str]:
        """List the contents of a directory."""

        base_name = str(pathlib.PurePosixPath(path_like)).replace("/", ".")
        sql = """
            SELECT
                path
            FROM code
            WHERE
                path LIKE $package_like
                AND path NOT LIKE $subpackage_like

            UNION

            SELECT
                DISTINCT substr(
                    path,
                    0,
                    length($package) + instr(substr(path, length($package) + 1), '/')
                )
            FROM code
            WHERE
                path LIKE $subpackage_like
            ;
        """

        results = self.connection.execute(
            sql,
            {
                "package": f"{base_name}/",
                "package_like": f"{base_name}/%",
                "subpackage_like": f"{base_name}/%/%",
            },
        ).fetchall()
        parsed_results: list[str] = []
        for result in results:
            if result[0].endswith("/__init__.py"):
                parsed_results.append(result[0].rpartition("/")[0])
            else:
                parsed_results.append(result[0])
        return parsed_results
