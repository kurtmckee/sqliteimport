..
    This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
    Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT


Integrating with flake8
#######################

If you rely on sqliteimport's auto-loading of ``.sqlite3`` files on the ``PYTHONPATH``,
importing sqliteimport is sufficient.

..  literalinclude:: example.py

However, flake8 will throw warning `F401`_,
indicating that the sqliteimport appears to be unused.

This can be addressed by adding a ``noqa: F401`` comment.

..  literalinclude:: example-noqa.py


..  Links
..  -----
..
..  _F401: https://flake8.pycqa.org/en/latest/user/error-codes.html
