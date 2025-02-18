# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import functools
import marshal
import sys

__all__ = [
    "marshal_dumps",
    "marshal_loads",
    "Traversable",
    "TraversableResources",
]

if sys.version_info >= (3, 13):
    # Python 3.13 introduced the `allow_code` parameter,
    # and it is mandatory for the sqliteimport use case.
    marshal_dumps = functools.partial(marshal.dumps, allow_code=True)
    marshal_loads = functools.partial(marshal.loads, allow_code=True)
else:
    marshal_dumps = marshal.dumps
    marshal_loads = marshal.loads

if sys.version_info >= (3, 11):
    # Python 3.11 moved some abstract base classes.
    from importlib.resources.abc import Traversable, TraversableResources
else:
    from importlib.abc import Traversable, TraversableResources
