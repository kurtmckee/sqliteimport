import contextlib
import importlib.machinery
import importlib.metadata
import importlib.resources
import sys
import types
import uuid

import pytest

import sqliteimport
import sqliteimport.accessor
import sqliteimport.bundler


@pytest.mark.parametrize(
    "import_name, version",
    (
        ("module_filesystem", "1.1.1"),
        ("module_sqlite", "2.2.2"),
    ),
)
def test_module(database, import_name, version):
    module = importlib.import_module(import_name)
    assert isinstance(module, types.ModuleType)
    assert module.x == "module"
    assert importlib.metadata.version(import_name) == version

    assert module.__name__ == import_name
    assert module.__doc__ is None
    if sys.version_info >= (3, 10):
        assert module.__annotations__ == {}
    else:
        # Python 3.9 doesn't have an `__annotations__` object at the module level.
        assert not hasattr(module, "__annotations__")

    if hasattr(module, "__cached__"):
        assert isinstance(module.__cached__, str)
    assert isinstance(module.__file__, str)
    assert module.__loader__ is not None
    assert module.__package__ == ""
    assert not hasattr(module, "__path__")

    # The Python documentation has strong recommendations for accessing these globals.
    # Ensure that imported modules can follow the strong recommendations.
    assert isinstance(module.__spec__, importlib.machinery.ModuleSpec)
    if hasattr(module, "__cached__"):
        assert module.__cached__ == module.__spec__.cached
    assert module.__file__ == module.__spec__.origin
    assert module.__loader__ == module.__spec__.loader
    assert module.__package__ == module.__spec__.parent
    assert module.__spec__.submodule_search_locations is None


@pytest.mark.parametrize(
    "import_name",
    (
        "package_filesystem",
        "package_sqlite",
    ),
)
def test_package(database, import_name):
    module = importlib.import_module(import_name)

    assert module.__name__ == import_name
    assert module.__doc__ is None
    if sys.version_info >= (3, 10):
        assert module.__annotations__ == {}
    else:
        # Python 3.9 doesn't have an `__annotations__` object at the module level.
        assert not hasattr(module, "__annotations__")

    if hasattr(module, "__cached__"):
        assert isinstance(module.__cached__, str)
    assert isinstance(module.__file__, str)
    assert module.__loader__ is not None
    assert module.__package__ == import_name
    assert hasattr(module, "__path__")

    # The Python documentation has strong recommendations for accessing these globals.
    # Ensure that imported modules can follow the strong recommendations.
    assert isinstance(module.__spec__, importlib.machinery.ModuleSpec)
    if hasattr(module, "__cached__"):
        assert module.__cached__ == module.__spec__.cached
    assert module.__file__ == module.__spec__.origin
    assert module.__loader__ == module.__spec__.loader
    assert module.__package__ == module.__spec__.parent
    assert isinstance(module.__spec__.submodule_search_locations, list)


@pytest.mark.parametrize(
    "import_name",
    (
        "package_filesystem",
        "package_sqlite",
    ),
)
def test_package_resources(database, import_name):
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


@pytest.mark.parametrize(
    "namespace, package, version",
    (
        ("namespace_filesystem", "plugin", "1.1.1"),
        ("namespace_sqlite", "plugin", "2.2.2"),
    ),
)
def test_namespace_package(database, namespace, package, version):
    module = importlib.import_module(f"{namespace}.{package}")
    assert isinstance(module.g, dict)
    assert importlib.metadata.version(f"{namespace}_{package}") == version

    assert module.__name__ == f"{namespace}.{package}"
    assert module.__doc__ is None
    if sys.version_info >= (3, 10):
        assert module.__annotations__ == {}
    else:
        # Python 3.9 doesn't have an `__annotations__` object at the module level.
        assert not hasattr(module, "__annotations__")

    if hasattr(module, "__cached__"):
        assert isinstance(module.__cached__, str)
    assert isinstance(module.__file__, str)
    assert module.__loader__ is not None
    assert module.__package__ == f"{namespace}.{package}"
    assert hasattr(module, "__path__")

    # The Python documentation has strong recommendations for accessing these globals.
    # Ensure that imported modules can follow the strong recommendations.
    assert isinstance(module.__spec__, importlib.machinery.ModuleSpec)
    if hasattr(module, "__cached__"):
        assert module.__cached__ == module.__spec__.cached
    assert module.__file__ == module.__spec__.origin
    assert module.__loader__ == module.__spec__.loader
    assert module.__package__ == module.__spec__.parent
    assert isinstance(module.__spec__.submodule_search_locations, list)


def test_distribution_finding(database):
    """Verify that sqliteimport doesn't discover packages it isn't responsible for."""

    name = f"p{uuid.uuid4().hex}"
    discovered = list(sqliteimport.importer.SqliteDistribution.discover(name=name))
    assert discovered == []
