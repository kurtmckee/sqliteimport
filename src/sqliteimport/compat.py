# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import functools
import marshal as marshal_
import sys
import types
import typing

__all__ = [
    "accommodate_python_39_from_package_behavior",
    "marshal",
    "Traversable",
    "TraversableResources",
]


if sys.version_info < (3, 13):
    # Python 3.13 introduced the `allow_code` parameter,
    # and it is mandatory for the sqliteimport use case.
    # Mimic the Python 3.13 marshal module's function signatures.
    @functools.wraps(marshal_.dumps)
    def marshal_dumps(value: types.CodeType, **_: typing.Any) -> bytes:
        return marshal_.dumps(value)

    @functools.wraps(marshal_.loads)
    def marshal_loads(value: bytes, **_: typing.Any) -> types.CodeType:
        return marshal_.loads(value)

    marshal = types.SimpleNamespace()
    marshal.dumps = marshal_dumps
    marshal.loads = marshal_loads
else:
    # No-op for Python 3.13 and higher.
    marshal = marshal_

if sys.version_info >= (3, 11):
    # Python 3.11 moved some abstract base classes.
    from importlib.resources.abc import Traversable, TraversableResources
else:
    from importlib.abc import Traversable, TraversableResources

T = typing.TypeVar("T")
if sys.version_info < (3, 10):
    # Python 3.9's `from_package()` implementation returns a `pathlib.Path` instance,
    # so the function must be patched to return a `Traversable` instance.
    #
    # This identity decorator function that must be applied to SqliteLoader.
    #
    # noinspection PyUnresolvedReferences,PyProtectedMember
    def accommodate_python_39_from_package_behavior(cls: type[T]) -> type[T]:
        import importlib._common  # type: ignore[import-not-found]

        original_from_package: typing.Callable[[types.ModuleType], Traversable] = (
            importlib._common.from_package
        )

        # noinspection PyUnresolvedReferences
        @functools.wraps(original_from_package)
        def _from_package(package: types.ModuleType) -> Traversable:
            spec = package.__spec__
            if spec is None:
                return original_from_package(package)

            loader = spec.loader
            if not isinstance(loader, cls):
                return original_from_package(package)
            return loader.get_resource_reader(spec.name).files()

        importlib._common.from_package = _from_package

        return cls

else:
    # Python 3.10 and higher have correct behavior so no patching is required.
    def accommodate_python_39_from_package_behavior(cls: type[T]) -> type[T]:
        return cls
