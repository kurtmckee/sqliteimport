import contextlib
import importlib.metadata
import importlib.resources
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


@pytest.mark.parametrize(
    "import_name, version",
    (
        ("module_filesystem", "1.1.1"),
        ("module_sqlite", "2.2.2"),
    ),
)
def test_module(database, import_name, version):
    module = importlib.import_module(import_name)
    assert module.x == "module"
    assert importlib.metadata.version(import_name) == version


@pytest.mark.parametrize(
    "import_name",
    (
        "package_filesystem",
        "package_sqlite",
    ),
)
def test_package(database, import_name):
    module = importlib.import_module(import_name)

    # Python 3.11 and 3.12 (but not 3.13) throw DeprecationWarning when calling
    # `importlib.resources.read_text()` and `importlib.resources.read_bytes()`.
    # These are caught, confirmed to match expectations, and wholly ignored.
    ignore_tempermental_warnings = contextlib.nullcontext()
    if sys.version_info[:2] in ((3, 11), (3, 12)):
        ignore_tempermental_warnings = pytest.warns(
            DeprecationWarning,
            match=(
                r"(open_text|read_text|read_binary) is deprecated. "
                r"Use files\(\) instead"
            ),
        )

    # Test resource access via `importlib.resources` helper functions.
    with ignore_tempermental_warnings:
        content_text = importlib.resources.read_text(module, "resource.txt")
        content_bytes = importlib.resources.read_binary(module, "resource.txt")
    assert content_text.strip() == "resource"
    assert content_bytes.strip() == b"resource"

    resource = importlib.resources.files(module) / "resource.txt"

    # Test in-memory resource access via the `.read_text()` and `.read_bytes()` methods.
    content_text = resource.read_text()
    content_bytes = resource.read_bytes()
    assert content_text.strip() == "resource"
    assert content_bytes.strip() == b"resource"

    # Test in-memory resource access via the `.open()` method.
    with resource.open("r") as file:
        content_text = file.read()
    with resource.open("rb") as file:
        content_bytes = file.read()
    assert content_text.strip() == "resource"
    assert content_bytes.strip() == b"resource"

    # Test extracting a file to disk via the `.as_file()` method.
    with importlib.resources.as_file(resource) as path:
        content_text = path.read_text()
        content_bytes = path.read_bytes()
    assert content_text.strip() == "resource"
    assert content_bytes.strip() == b"resource"


@pytest.mark.parametrize(
    "import_name",
    (
        "package_filesystem.shift_jis",
        "package_sqlite.shift_jis",
    ),
)
def test_package_shift_jis(database, import_name):
    module = importlib.import_module(import_name)

    assert module.a == "あ"


@pytest.mark.parametrize(
    "import_name",
    (
        "package_filesystem.あ",
        "package_sqlite.あ",
    ),
)
def test_package_unicode_filename(database, import_name):
    module = importlib.import_module(import_name)

    assert module.success == "unicode-filename"
