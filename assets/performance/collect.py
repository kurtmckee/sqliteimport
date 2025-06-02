# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import itertools
import json
import pathlib
import typing

import click

from . import LOG_PATHS, PACKAGE_PATHS, STATS, CodeType, Importer, Measurement


@click.command()
def collect() -> None:
    """
    Collect import and sizing stats and write them to a JSON file.
    """

    stats = {
        Measurement.time: parse_import_log(),
        Measurement.size: get_size_stats(),
    }
    output_path = STATS / "stats.json"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(json.dumps(stats, indent=2, sort_keys=True))


def parse_import_log() -> dict[str, dict[str, dict[str, int]]]:
    """Parse an import log to extract per-module cumulative import times (in µs)."""

    stats: dict[str, dict[str, dict[str, int]]] = {}
    for importer, code_type in itertools.product(Importer, CodeType):
        stats.setdefault(code_type, {})[importer] = {"-cumulative_us": 0}
        file = LOG_PATHS[importer][code_type]
        if not file.is_file():
            click.echo(f"{file} not found")
            continue

        content = file.read_text()

        for _, cumulative_us, module in split_columns(content):
            if module.startswith(" "):
                # The module is an indented submodule.
                # Only top-level modules are recorded here.
                continue
            stats[code_type][importer][module] = cumulative_us
            stats[code_type][importer]["-cumulative_us"] += cumulative_us

    return stats


def split_columns(text: str) -> typing.Iterator[tuple[int, int, str]]:
    for line in text.splitlines():
        prefix, _, remainder = line.partition(": ")
        if prefix != "import time":
            continue
        try:
            self, cumulative, module = remainder.split(" | ")
            yield int(self.strip()), int(cumulative.strip()), module.rstrip()
        except (TypeError, ValueError):
            continue


def get_size_stats() -> dict[Importer, dict[CodeType, int]]:
    """Get the size of items on disk.

    This only considers the raw sum of the sizes of files on disk.
    It does not, for example, calculate the size of the filesystem blocks
    that are consumed by individual files.
    """

    importer: Importer
    code_type: CodeType

    sizes: dict[Importer, dict[CodeType, int]] = {
        importer: {code_type: -1 for code_type in CodeType} for importer in Importer
    }
    for importer, code_type in itertools.product(Importer, CodeType):
        path = PACKAGE_PATHS[importer][code_type]
        if path.is_dir():
            sizes[importer][code_type] = get_directory_size(path, code_type)
        elif path.is_file():
            sizes[importer][code_type] = path.stat().st_size
        else:
            typing.assert_never((importer, code_type))

    return sizes


def get_directory_size(directory: pathlib.Path, code_type: CodeType) -> int:
    """Get the size of a directory.

    PEP3147-compatible ``*.pyc`` files will be included in the calculation
    if the *code_type* indicates byte code.
    """

    size = 0

    directories = [directory]
    while directories:
        directory = directories.pop()
        for path in directory.glob("*"):
            if path.is_dir():
                # Skip `__pycache__/` directories unless calculating byte code size.
                if path.name == "__pycache__" and code_type != CodeType.bytecode:
                    continue
                directories.append(path)

            elif path.is_file():
                # Skip `*.pyc` files unless calculating byte code size.
                # Even then, the `*.pyc` files must be in a `__pycache__/` directory.
                if path.suffix == ".pyc":
                    if not (
                        code_type == CodeType.bytecode
                        and path.parent.name == "__pycache__"
                    ):
                        continue

                size += path.stat().st_size

    return size
