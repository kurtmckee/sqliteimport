..
    This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
    Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT


Integrating with ruff
#####################

If you rely on sqliteimport's auto-loading of ``.sqlite3`` files on the ``PYTHONPATH``,
the ``import sqliteimport`` line needs to appear before third-party modules:

..  literalinclude:: assets/example.py

However, ruff copies isort's behavior and will sort these lines alphabetically,
breaking the imports:

..  literalinclude:: assets/example-bad-sort.py

It also copies flake8's behavior and will throw an ``F401`` error
to flag that the ``sqliteimport`` module appears to be unused.

There are several ways to resolve these issues.


Import sorting: custom section
==============================

You can configure ruff to put sqliteimport into a custom section
that always sorts before third-party packages:

..  literalinclude:: assets/custom-section/pyproject.toml
    :caption: ``pyproject.toml``
    :language: toml

..  literalinclude:: assets/custom-section/ruff.toml
    :caption: ``ruff.toml``
    :language: toml

Result:

..  literalinclude:: assets/custom-section/sorted.py


Import sorting: ``force-to-top``
================================

You can force sqliteimport to the top of the third party section:

..  literalinclude:: assets/force-to-top/pyproject.toml
    :caption: ``pyproject.toml``
    :language: toml
    :lines: 1-2

..  literalinclude:: assets/force-to-top/ruff.toml
    :caption: ``ruff.toml``
    :language: toml
    :lines: 1-2

Result:

..  literalinclude:: assets/force-to-top/sorted.py


``F401`` errors: Ignore it
==========================

You can add a comment to the end of the line to disable ruff's flake8 ``F401`` error:

..  literalinclude:: assets/F401/example.py
    :lines: 1-7
