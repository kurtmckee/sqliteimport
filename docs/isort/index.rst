..
    This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
    Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT


Integrating with isort
######################

If you rely on sqliteimport's auto-loading of ``.sqlite3`` files on the ``PYTHONPATH``,
the ``import sqliteimport`` line needs to appear before third-party modules:

..  literalinclude:: assets/example.py

However, isort would normally sort these lines alphabetically and break your imports:

..  literalinclude:: assets/example-bad-sort.py

There are two ways to address this.


Custom section
==============

You can configure isort to put sqliteimport into a custom section
that always sorts before third-party packages:

..  literalinclude:: assets/custom-section/config.toml
    :caption: ``pyproject.toml``
    :language: toml

..  literalinclude:: assets/custom-section/config.ini
    :caption: ``.isort.cfg``
    :language: ini

Result:

..  literalinclude:: assets/custom-section/sorted.py


``force_to_top``
================

You can force sqliteimport to the top of the third party section:

..  literalinclude:: assets/force-to-top/config.toml
    :caption: ``pyproject.toml``
    :language: toml

..  literalinclude:: assets/force-to-top/config.ini
    :caption: ``.isort.cfg``
    :language: ini

Result:

..  literalinclude:: assets/force-to-top/sorted.py
