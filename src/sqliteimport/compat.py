# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import functools
import marshal as marshal_
import sys
import types
import typing

__all__ = [
    "compression",
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
        return typing.cast(types.CodeType, marshal_.loads(value))

    marshal = types.SimpleNamespace()
    marshal.dumps = marshal_dumps
    marshal.loads = marshal_loads
else:
    # No-op for Python 3.13 and higher.
    marshal = marshal_

if sys.version_info >= (3, 11):
    # Python 3.11 moved some abstract base classes.
    from importlib.resources.abc import Traversable
    from importlib.resources.abc import TraversableResources
else:
    from importlib.abc import Traversable
    from importlib.abc import TraversableResources


if sys.version_info < (3, 14):
    # Python 3.14 introduced the top-level `compression` module,
    # which contains compression libraries like `lzma`.
    # Mimic the Python 3.14 compression module namespace.
    import lzma

    compression = types.SimpleNamespace()
    compression.lzma = lzma
else:
    # No-op for Python 3.14 and higher.
    import compression.lzma
