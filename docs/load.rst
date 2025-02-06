..
    This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
    Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT


Loading sqliteimport
####################

sqliteimport must be imported and configured
before packages stored in sqlite can be imported.


Automatic loading
=================

If you use the ``PYTHONPATH`` environment variable to point to a sqlite database
then importing sqliteimport is sufficient to load packages from the database.


..  code-block:: shell
    :caption: Linux/macos

    export PYTHONPATH=packages.sqlite3

    python -m my_tool_or_package
    ./my_tool_or_package


..  code-block:: powershell
    :caption: Windows Powershell

    $env:PYTHONPATH="packages.sqlite3"

    python -m my_tool_or_package
    & my_tool_or_package
