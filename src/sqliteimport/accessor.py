# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import lzma
import pathlib
import sqlite3
import types
import typing

from .compat import marshal
from .errors import FileNotFoundInDatabaseError
from .util import get_magic_number, get_python_identifier


class Accessor:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.find_spec_table = "code"
        if (
            "magic_numbers" in self.get_tables()
            and get_magic_number() in self.get_magic_numbers()
        ):
            self.find_spec_table = self.get_bytecode_table_name(get_magic_number())

    def get_tables(self) -> list[str]:
        """List all the tables in the database."""

        query = """
            SELECT
                name
            FROM sqlite_master
            WHERE type='table'
            ;
        """
        return [row[0] for row in self.connection.execute(query).fetchall()]

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
                contents text
            );

            CREATE INDEX fullname_index ON code (fullname);

            CREATE TABLE magic_numbers (
                magic_number INTEGER,
                python_identifier TEXT
            );
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

    def get_magic_numbers(self) -> dict[int, str]:
        """Get the magic numbers of the already-compiled bytecodes in the database."""

        magic_numbers = self.connection.execute(
            """
            SELECT
                magic_number,
                python_identifier
            FROM
                magic_numbers
            ;
            """
        ).fetchall()
        return {row[0]: row[1] for row in magic_numbers}

    def add_directory(self, directory: pathlib.Path) -> None:
        """Add an importable directory (such as a namespace) to the database."""

        fullname = str(directory)
        is_package = True
        contents = b""

        self.connection.execute(
            """
            INSERT INTO code (fullname, path, is_package, contents)
            VALUES (?, ?, ?, ?);
            """,
            (
                fullname.replace("/", ".").replace("\\", "."),
                str(pathlib.PurePosixPath(directory)),
                is_package,
                compress(contents),
            ),
        )

    def add_file(self, directory: pathlib.Path, file: pathlib.Path) -> None:
        """Add a file to the database."""

        fullname = ""
        is_package = False
        contents = (directory / file).read_bytes()

        if file.name == "__init__.py":
            is_package = True
            # "x/y/__init__.py" -> "x/y"
            fullname = str(file.parent)
        elif file.suffix == ".py":
            # "x/y/z.py" -> "x/y/z"
            fullname = str(file.with_suffix(""))

        self.connection.execute(
            """
            INSERT INTO code (fullname, path, is_package, contents)
            VALUES (?, ?, ?, ?);
            """,
            (
                fullname.replace("/", ".").replace("\\", "."),
                str(pathlib.PurePosixPath(file)),
                is_package,
                compress(contents),
            ),
        )

    @staticmethod
    def get_bytecode_table_name(magic_number: int) -> str:
        """Generate a bytecode table name."""

        return f"bytecode_{magic_number}"

    def create_bytecode_table(self, magic_number: int) -> None:
        """Create a compiled bytecode table."""

        table_name = self.get_bytecode_table_name(magic_number)
        self.connection.executescript(
            f"""
            CREATE TABLE {table_name}
            (
                fullname TEXT,
                path TEXT,
                is_package BOOLEAN,
                contents TEXT
            );

            CREATE INDEX {table_name}_fullname_index ON {table_name} (fullname);
            """
        )

    def add_bytecode(
        self, magic_number: int, fullname: str, path: str, is_package: bool, code: bytes
    ) -> None:
        """Add compiled bytecode to the database for a given magic number."""

        table_name = f"bytecode_{magic_number}"
        self.connection.execute(
            f"""
            INSERT INTO {table_name} (fullname, path, is_package, contents)
            VALUES (?, ?, ?, ?);
            """,
            (
                fullname,
                path,
                is_package,
                compress(code),
            ),
        )

    def mark_magic_number(self, magic_number: int) -> None:
        """Mark that bytecode has been fully compiled for a given magic number."""

        self.connection.execute(
            """
            INSERT INTO magic_numbers (magic_number, python_identifier)
            VALUES ($magic_number, $python_identifier)
            ;
            """,
            {
                "magic_number": magic_number,
                "python_identifier": get_python_identifier(),
            },
        )

    def find_spec(
        self, fullname: str
    ) -> tuple[str, bytes | types.CodeType, bool] | None:
        result: tuple[str, bytes, bool] | None = self.connection.execute(
            f"""
            SELECT
                path,
                contents,
                is_package
            FROM {self.find_spec_table}
            WHERE fullname = ?
            ;
            """,
            (fullname,),
        ).fetchone()
        if result is None:
            return None
        path, code, is_package = result
        code = decompress(code)

        # Source code
        if self.find_spec_table == "code":
            return path, code, is_package

        # Byte code
        return path, marshal.loads(code, allow_code=True), is_package

    @typing.overload
    def get_file(self, *, path: str) -> bytes: ...

    @typing.overload
    def get_file(self, *, fullname: str) -> bytes: ...

    def get_file(
        self, *, path: str | None = None, fullname: str | None = None
    ) -> bytes:
        contents: bytes
        if path:
            cursor = self.connection.execute(
                """
                SELECT
                    contents
                FROM code
                WHERE path LIKE ?;
                """,
                (path,),
            )
        else:  # fullname
            cursor = self.connection.execute(
                """
                SELECT
                    contents
                FROM code
                WHERE fullname LIKE ?;
                """,
                (fullname,),
            )

        try:
            contents = cursor.fetchone()[0]
        except TypeError:
            filename = str(path or fullname)
            database_path = self.get_database_path(self.connection)
            raise FileNotFoundInDatabaseError(filename, database_path)

        return decompress(contents)

    def find_distributions(self, name: str | None) -> typing.Generator[str]:
        if name is not None:
            path_pattern = f"{name}-%.dist-info/METADATA"
        else:
            path_pattern = "%.dist-info/METADATA"

        sql = """
            SELECT
                path
            FROM code
            WHERE
                path LIKE $path_pattern
            ;
        """

        cursor = self.connection.execute(
            sql,
            {"path_pattern": path_pattern},
        )
        rows = cursor.fetchall()
        if rows is None:
            return

        path: str
        for (path,) in rows:
            module, _, _ = path.partition("-")
            if module.isidentifier():
                yield module

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

    def iter_source_code(self) -> typing.Generator[tuple[str, str, bool, bytes]]:
        cursor = self.connection.cursor()
        iterable = cursor.execute(
            """
            SELECT
                fullname,
                path,
                is_package,
                contents
            FROM code
            WHERE path LIKE '%.py'
            ;
            """
        )
        row: tuple[str, str, bool, bytes]
        for row in iterable:
            fullname, path, is_package, contents = row
            yield fullname, path, is_package, decompress(contents)

    def iter_package_metadata(self) -> typing.Generator[bytes]:
        """Find and return all METADATA files in `.dist-info/` directories."""

        cursor = self.connection.cursor()
        iterable = cursor.execute(
            """
            SELECT
                contents
            FROM code
            WHERE path LIKE '%.dist-info/METADATA'
            ;
            """
        )
        row: tuple[bytes]
        for row in iterable:
            contents = row[0]
            yield decompress(contents)

    def get_database_metadata(self) -> list[tuple[str, str]]:
        """Get all rows from the ``sqliteimport`` table."""

        sql = """
            SELECT
                field,
                value
            FROM sqliteimport
            ;
        """
        return self.connection.execute(sql).fetchall()


def compress(data: bytes) -> bytes:
    return lzma.compress(
        data,
        format=lzma.FORMAT_RAW,
        filters=[{"id": lzma.FILTER_LZMA2, "preset": 0}],
    )


def decompress(data: bytes) -> bytes:
    return lzma.decompress(
        data,
        format=lzma.FORMAT_RAW,
        filters=[{"id": lzma.FILTER_LZMA2, "preset": 0}],
    )
