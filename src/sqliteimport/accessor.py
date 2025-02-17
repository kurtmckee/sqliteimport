# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import marshal
import pathlib
import sqlite3
import sys
import types


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

    @staticmethod
    def get_database_path(database: sqlite3.Connection) -> str:
        """Get the path to the database, as reported by sqlite itself.

        sqlite returns an empty string if the database is not associated with a file.
        """

        path: str
        _, _, path = database.execute("PRAGMA database_list;").fetchone()
        return path

    def add_file(self, directory: pathlib.Path, file: pathlib.Path) -> None:
        """Add a file to the database."""

        fullname = ""
        is_package = False
        contents = (directory / file).read_bytes()

        # Source code
        if file.name == "__init__.py":
            is_package = True
            # "x/y/__init__.py" -> "x/y"
            fullname = str(file.parent)
        elif file.suffix == ".py":
            # "x/y/z.py" -> "x/y/z"
            fullname = str(file.with_suffix(""))

        # Bytecode
        elif file.name == f"__init__.{sys.implementation.cache_tag}.pyc":
            is_package = True
            # "x/y/__pycache__/__init__.cpython-xyz.pyc" -> "x/y"
            fullname = str(file.parent.parent)
        elif file.suffix == ".pyc":
            suffix_length = sum(len(suffix) for suffix in file.suffixes)
            # "x/y/__pycache__/z.cpython-xyz.pyc" -> "x/y/z"
            fullname = str(file.parent.parent / file.name[:-suffix_length])

        self.connection.execute(
            """
            INSERT INTO code (fullname, path, is_package, source)
            VALUES (?, ?, ?, ?);
            """,
            (
                fullname.replace("/", ".").replace("\\", "."),
                str(pathlib.PurePosixPath(file)),
                is_package,
                contents,
            ),
        )

    def find_spec(self, fullname: str) -> tuple[bytes | types.CodeType, bool] | None:
        result: tuple[bytes, bool] | None = self.connection.execute(
            """
            SELECT
                source,
                is_package
            FROM code
            WHERE fullname = ?
            ORDER BY
                LENGTH(path) DESC
            ;
            """,
            (fullname,),
        ).fetchone()
        if result is None:
            return None

        # Byte code
        code, is_package = result
        if code.startswith(importlib.util.MAGIC_NUMBER):
            return marshal.loads(code[16:], allow_code=True), is_package

        # Source
        return result

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
