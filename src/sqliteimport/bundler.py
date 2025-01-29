import pathlib

import sqliteimport.accessor


def bundle(directory: pathlib.Path, accessor: sqliteimport.accessor.Accessor) -> None:
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
        is_package = (directory / file / "__init__.py").exists()
        print(f"{'* ' if is_package else '  '} {file}")
        if (directory / file).is_dir():
            continue
        accessor.add_file(directory, file)
