import contextlib
import pathlib
import sqlite3
import sys

import pytest

import sqliteimport
import sqliteimport.accessor
import sqliteimport.bundler

installed_projects = pathlib.Path(__file__).parent / "installed-projects"
sys.path.append(str(installed_projects / "filesystem"))


@pytest.fixture(scope="session")
def database():
    with sqlite3.connect(":memory:") as connection:
        accessor = sqliteimport.accessor.Accessor(connection)
        accessor.initialize_database()
        sqliteimport.bundler.bundle(installed_projects / "sqlite", accessor)
        sqliteimport.load(connection)

        yield connection


@pytest.fixture(scope="session")
def ignore_tempermental_deprecations():
    # Between 3.11 and 3.12.9, Python would throw DeprecationWarning when calling
    # `importlib.resources.read_text()` and `importlib.resources.read_bytes()`.
    # These are caught, confirmed to match expectations, and wholly ignored.
    ignore_tempermental_warnings = contextlib.nullcontext()
    if (3, 11) < sys.version_info[:3] <= (3, 12, 9):
        ignore_tempermental_warnings = pytest.warns(
            DeprecationWarning,
            match=(
                r"(open_text|read_text|read_binary) is deprecated. "
                r"Use files\(\) instead"
            ),
        )

    return ignore_tempermental_warnings
