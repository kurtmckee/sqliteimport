# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import pathlib

from .accessor import Accessor


def bundle(directory: pathlib.Path, accessor: Accessor) -> None:
    """Bundle files in a directory into a database."""

    paths: list[pathlib.Path] = list(directory.glob("*"))
    files = []
    for path in paths:
        rel_path = path.relative_to(directory)
        if rel_path.suffix in {".so"}:
            continue
        if rel_path.name == "__pycache__":
            continue
        if str(rel_path) == "bin":
            continue
        if path.is_dir():
            files.append(rel_path)
            paths.extend(path.glob("*"))
        else:
            files.append(rel_path)

    for file in sorted(files):
        path = directory / file
        if path.is_file():
            print(f"   {file}")
            accessor.add_file(directory, file)
        elif path.is_dir():
            # Directories *might* be importable namespaces.
            # If so, the current database design requires an entry in the database.

            # Ignore directories that appear to be true packages.
            if (path / "__init__.py").exists():
                continue

            # Ignore directories that cannot be imported.
            if not all(part.isidentifier() for part in file.parts):
                continue

            print(f"*  {file}")
            accessor.add_directory(file)
