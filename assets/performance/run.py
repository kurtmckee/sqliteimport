# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import os
import pathlib
import subprocess

import click

from . import LOG_PATHS
from . import PACKAGE_PATHS
from . import REPO_ROOT
from . import CodeType
from . import Importer


@click.command("run", no_args_is_help=True)
@click.option(
    "--importer",
    type=Importer,
    required=True,
    help=f"The importer to use. Valid importers are: {', '.join(Importer)}.",
)
@click.option(
    "--code-type",
    type=CodeType,
    required=True,
    help=f"The code type to use. Valid code types are: {', '.join(CodeType)}.",
)
@click.argument(
    "target",
    type=pathlib.Path,
    metavar="PYTHON_FILE",
)
def run(importer: Importer, code_type: CodeType, target: pathlib.Path) -> None:
    """
    Run the given PYTHON_FILE, backed by the given importer and code type.

    NOTE: If the filesystem importer is used and bytecode has already been compiled,
    there is no technical way to force source-only importing.
    Therefore, it is up to the caller to ensure that bytecode is unavailable
    when attempting to test the filesystem importer with source code only.
    """

    command = ["python", "-vv", str(target)]
    python_paths = [str(PACKAGE_PATHS[importer][code_type])]
    # Specifically for sqliteimport, add the `site_customizer` to the Python path.
    # This allows sqliteimport to be loaded automatically and transparently
    # without requiring changes to the *target* script.
    if importer == Importer.sqliteimport:
        python_paths.insert(0, str(REPO_ROOT / "assets/performance/site_customizer"))

    environment = {
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPROFILEIMPORTTIME": "1",
        "PYTHONPATH": os.pathsep.join(python_paths),
    }
    process = subprocess.run(command, env=environment, capture_output=True)
    if process.returncode:
        print(process.returncode)
    if process.stdout:
        print(process.stdout.decode("utf-8", errors="replace"))

    LOG_PATHS[importer][code_type].write_bytes(process.stderr)
