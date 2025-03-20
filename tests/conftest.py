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
