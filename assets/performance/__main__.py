# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import pathlib
import sys

import click

# Add this directory to the Python path so imports work.
assets = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(assets))


if __name__ == "__main__":
    from performance.clean import clean
    from performance.collect import collect
    from performance.compile import compile_
    from performance.generate import generate
    from performance.plot import plot
    from performance.run import run

    group = click.Group()
    group.add_command(clean)
    group.add_command(collect)
    group.add_command(compile_)
    group.add_command(generate)
    group.add_command(plot)
    group.add_command(run)
    group()
