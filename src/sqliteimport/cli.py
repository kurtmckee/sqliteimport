import pathlib
import sqlite3
import sys
import textwrap

from . import bundler
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

    with sqlite3.connect(database) as connection:
        accessor = Accessor(connection)
        accessor.initialize_database()

        bundler.bundle(directory, accessor)
        connection.commit()
