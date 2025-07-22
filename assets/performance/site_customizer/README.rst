..
    This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
    Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT

The performance testing script relies on this directory
to ensure that sqliteimport can auto-load databases.

It does this by including this directory in the ``PYTHONPATH`` environment variable
when executing a given script file.

Python will automatically search for a ``sitecustomize.py`` file during startup
and will find that file in this directory.

When it loads, ``sitecustomize.py`` will remove this directory
from the list of Python paths to search, and then import sqliteimport.

For more information about ``sitecustomize.py``,
please see the Python `site module documentation`_.


..  Links
..  -----
..
..  _site module documentation: https://docs.python.org/3/library/site.html
