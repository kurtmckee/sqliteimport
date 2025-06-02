# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import pathlib
import shutil
import subprocess

import click

from . import PACKAGE_DIRECTORY


@click.command(no_args_is_help=True)
@click.option(
    "--requirement",
    "-r",
    type=click.Path(dir_okay=False, exists=True),
    help=(
        "Generate the package directory by running `pip install -r REQUIREMENTS.TXT`."
    ),
)
@click.option(
    "--artificial",
    "-a",
    is_flag=True,
    help=(
        "Generate a massive, artificially-constructed package"
        " in the package directory."
    ),
)
def generate(requirement: pathlib.Path | None, artificial: bool) -> None:
    """
    Generate the directory of packages that will be used for performance testing.

    `--requirement` and `--artificial` are mutually exclusive arguments,
    but one of the two is required.
    """

    if requirement and artificial:
        click.echo("`--requirements` and `--artificial` are mutually exclusive.")
        raise SystemExit(2)

    if PACKAGE_DIRECTORY.exists():
        shutil.rmtree(PACKAGE_DIRECTORY)

    if artificial:
        print("This will generate ~1,300 files and consume ~1.2GB of disk space.")
        click.confirm("Continue?", default=False, abort=True)

        construct_package(PACKAGE_DIRECTORY, depth=50)
    else:
        pip_install(PACKAGE_DIRECTORY, requirement=requirement)


def construct_package(target: pathlib.Path, *, depth: int) -> None:
    letters = "bcdefghijklmnopqrstuvwxyz"  # 'a' is deliberately skipped.

    target.mkdir(exist_ok=True)
    path = target / "/".join("a" for _ in range(depth))
    path.mkdir(parents=True, exist_ok=True)

    # Create a deep and wide chain of imports.
    first_line = "from . import a"
    other_lines = [f"from . import {letter}" for letter in letters]

    code = "\n".join(["#" * 100 for _ in range(10_000)])

    current_path = path
    while current_path != target:
        print(current_path)
        (current_path / "__init__.py").write_text("\n".join([first_line] + other_lines))
        for letter in letters:
            (current_path / f"{letter}.py").write_text(code)
        current_path = current_path.parent

    # Overwrite the deepest __init__.py.
    (path / "__init__.py").write_text("\n".join([f"depth = {depth}"] + other_lines))


def pip_install(target: pathlib.Path, *, requirement: pathlib.Path) -> None:
    cmd = [
        "pip",
        "install",
        "--no-compile",
        "--target",
        target,
        "--requirement",
        requirement,
    ]
    subprocess.check_call(cmd)
