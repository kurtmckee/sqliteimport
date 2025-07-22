# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import subprocess
import typing

import click

from . import PACKAGE_DIRECTORY
from . import PACKAGE_PATHS
from . import CodeType
from . import Importer


@click.command("compile", no_args_is_help=True)
@click.option(
    "--importer",
    type=Importer,
    required=True,
    help=f"The importer to compile for. Valid importers are: {', '.join(Importer)}.",
)
def compile_(importer: Importer) -> None:
    """
    Compile source code to byte code for a given importer.
    """

    if importer == Importer.filesystem:
        compile_for_filesystem()
    elif importer == Importer.zipimport:
        compile_for_zipimport()
    elif importer == Importer.sqliteimport:
        compile_for_sqliteimport()
    else:
        typing.assert_never(importer)


def compile_for_filesystem():
    """Compile bytecode in PEP3147-compatible `__pycache__/` subdirectories."""

    cmd = ["python", "-m", "compileall", PACKAGE_DIRECTORY]
    subprocess.check_call(cmd)


def compile_for_zipimport():
    """Compile bytecode to pre-PEP3147-compatible `*.pyc` files."""

    cmd = ["python", "-m", "compileall", "-b", PACKAGE_DIRECTORY]
    subprocess.check_call(cmd)


def compile_for_sqliteimport():
    """Create a sqliteimport database and compile the code to bytecode."""

    database_path = PACKAGE_PATHS[Importer.sqliteimport][CodeType.bytecode]
    if database_path.exists():
        database_path.unlink()

    cmd = ["sqliteimport", "bundle", PACKAGE_DIRECTORY, database_path]
    subprocess.check_call(cmd)
    cmd = ["sqliteimport", "compile", database_path]
    subprocess.check_call(cmd)
