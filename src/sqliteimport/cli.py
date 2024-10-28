import pathlib
import sqlite3
import sys
import textwrap

from .accessor import Accessor

try:
    import click
except ImportError:
    print(
        textwrap.dedent(
            """
            sqliteimport is not installed with CLI support.

            This is typically resolved by adding '[cli]' to the end of the package name
            when installing sqliteimport. For example:

                python -m pip install sqliteimport[cli]
            """
        )
    )
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

    paths: list[pathlib.Path] = list(directory.glob("*"))
    files = []
    for path in paths:
        rel_path = path.relative_to(directory)
        if rel_path.suffix in (".dist-info", ".so"):
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

    connection = sqlite3.connect(database)
    accessor = Accessor(connection)
    accessor.initialize_database()

    for file in sorted(files):
        is_package = (directory / file / "__init__.py").exists()
        print(f"{'* ' if is_package else '  '} {file}")
        if (directory / file).is_dir():
            continue
        accessor.add_file(directory, file)

    connection.commit()
    connection.close()
