import pathlib
import sqlite3
import sys
import textwrap

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
            files.append((rel_path, (path / "__init__.py").exists()))
            paths.extend(path.glob("*"))
        else:
            files.append((rel_path, False))

    connection = sqlite3.connect(database)
    connection.execute(
        """
        CREATE TABLE code (
            fullname text,
            path text,
            is_package boolean,
            source text
        );
        """
    )

    for file, is_package in sorted(files):
        print(f"{'* ' if is_package else '  '} {file}")
        if (directory / file).is_dir():
            continue
        fullname = file.parent if file.name == "__init__.py" else file.with_suffix("")
        is_package = file.name == "__init__.py"
        connection.execute(
            """
            INSERT INTO code (fullname, path, is_package, source)
            VALUES (?, ?, ?, ?);
            """,
            (
                str(fullname).replace("/", ".").replace("\\", "."),
                str(file),
                is_package,
                (directory / file).read_text(),
            ),
        ).fetchone()

    connection.commit()
    connection.close()
