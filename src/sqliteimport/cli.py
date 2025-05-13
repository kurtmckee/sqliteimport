# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import itertools
import pathlib
import sqlite3
import sys
import textwrap

from . import bundler, compiler
from .accessor import Accessor
from .util import get_magic_number

try:
    import click
    import prettytable
except ImportError:
    message = """
        sqliteimport is not installed with CLI support.

        This is typically resolved by adding '[cli]' to the end of the package name
        when installing sqliteimport. Example commands that may resolve this:

        *   python -m pip install sqliteimport[cli]
        *   pipx install sqliteimport[cli]
    """

    print(textwrap.dedent(message), file=sys.stderr)
    sys.exit(2)


group = click.Group()


@group.command(no_args_is_help=True)
@click.argument(
    "directory", type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path)
)
@click.argument(
    "database", type=click.Path(dir_okay=False, file_okay=False, path_type=pathlib.Path)
)
def bundle(directory: pathlib.Path, database: pathlib.Path) -> None:
    """Bundle a directory containing Python code into a sqlite database.

    The directory can be generated using a package installer like pip.
    For example:

    \b
        pip install --target=DIRECTORY --requirement=path/to/requirements.txt
    """

    with sqlite3.connect(database) as connection:
        accessor = Accessor(connection)
        accessor.initialize_database()

        bundler.bundle(directory, accessor)
        connection.commit()


@group.command(name="compile", no_args_is_help=True)
@click.argument(
    "database", type=click.Path(dir_okay=False, file_okay=True, path_type=pathlib.Path)
)
def compile_(database: pathlib.Path) -> None:
    """Compile the source code in an existing database into bytecode.

    This results in a significant performance improvement.
    Note, though, that the bytecode is highly sensitive to the Python interpreter
    used to compile the code, so other Python interpreters will not benefit from this
    unless the source code is compiled for other Python interpreters, too.

    For example, if this command is run on Python 3.13,
    but the application can run on other Python versions,
    only Python 3.13 interpreters will benefit from the bytecode.

    Therefore, this command should be run on all Python versions that are supported
    by the application importing from the database.
    """

    with sqlite3.connect(database) as connection:
        accessor = Accessor(connection)
        existing_magic_numbers = accessor.get_magic_numbers()
        if get_magic_number() in existing_magic_numbers:
            identifier = existing_magic_numbers[get_magic_number()]
            msg = [
                "The source code in the database has already been compiled",
                f"for magic number {get_magic_number()} ({identifier})",
            ]
            click.echo("\n".join(msg))
            sys.exit(0)

        compiler.compile_bytecode(accessor)
        connection.commit()


@group.command(name="describe", no_args_is_help=True)
@click.argument(
    "database", type=click.Path(dir_okay=False, file_okay=True, path_type=pathlib.Path)
)
def describe(database: pathlib.Path) -> None:
    """Show information about the given database."""

    table = prettytable.PrettyTable()
    table.set_style(prettytable.TableStyle.DEFAULT)

    with sqlite3.connect(database) as connection:
        accessor = Accessor(connection)

        database_metadata = accessor.get_database_metadata()
        table.align = "l"
        table.field_names = ("Field", "Value")
        table.add_rows(database_metadata)  # type: ignore[arg-type]
        print("Database info:")
        print()
        print(textwrap.indent(str(table), "    "))

        magic_numbers = accessor.get_magic_numbers()
        print()
        if magic_numbers:
            table.clear()
            table.field_names = ("Magic Number", "Python interpreter")
            table.add_rows(list(magic_numbers.items()))  # type: ignore[arg-type]
            table.align = "l"
            print("The source code has been pre-compiled to bytecode.")
            print()
            print("The bytecode magic numbers are shown below,")
            print("along with the Python interpreter used for compilation:")
            print()
            print(textwrap.indent(str(table), "    "))
        else:
            print("The source code has not been pre-compiled to bytecode.")

        lines: list[list[str]] = []
        for metadata_raw in accessor.iter_package_metadata():
            metadata = metadata_raw.decode("utf-8", errors="ignore")
            name = ""
            version = ""
            for line in itertools.takewhile(lambda s: bool(s), metadata.splitlines()):
                if line.startswith("Name: "):
                    name = line[len("Name: ") :].strip()
                elif line.startswith("Version: "):
                    version = line[len("Version: ") :].strip()
            if name and version:
                lines.append([name, version])

        print()
        if lines:
            table.clear()
            table.field_names = ("Package", "Version")
            table.add_rows(lines)
            table.align = "l"
            print("The following packages are installed in the database:")
            print()
            print(textwrap.indent(str(table), "    "))
        else:
            print("No installed packages were found.")
