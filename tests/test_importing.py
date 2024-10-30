import importlib.metadata
import pathlib
import sqlite3
import sys

import pytest

import sqliteimport
import sqliteimport.accessor
import sqliteimport.bundler

installed_projects = pathlib.Path(__file__).parent / "installed-projects"
sys.path.append(str(installed_projects / "filesystem"))


@pytest.fixture(scope="module")
def database():
    with sqlite3.connect(":memory:") as connection:
        accessor = sqliteimport.accessor.Accessor(connection)
        accessor.initialize_database()
        sqliteimport.bundler.bundle(installed_projects / "sqlite", accessor)
        sqliteimport.load(connection)

        yield connection


def test_module(database):
    import module_filesystem

    assert module_filesystem.x == "module"
    assert importlib.metadata.version("module_filesystem") == "1.1.1"

    import module_sqlite

    assert module_sqlite.x == "module"
    assert importlib.metadata.version("module_sqlite") == "2.2.2"
