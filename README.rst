..
    This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
    Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT


..  image:: https://raw.githubusercontent.com/kurtmckee/sqliteimport/dfd7095f2df8d6e9249889dd85f102027d1a6cfb/docs/_static/banner.png
    :alt: sqlite import: Import Python code from sqlite databases.

-------------------------------------------------------------------------------

Demo usage example, using ``demo.py`` in `the sqliteimport repository`_:

..  code-block:: bash

    # Ensure sqliteimport is installed with the 'cli' extra.
    pip install sqliteimport[cli]

    # Install 'requests' in a standalone directory.
    pip install --target=sample requests

    # Generate a sqlite database containing the installed packages.
    sqliteimport bundle sample sample.sqlite3

    # Demonstrate that importing from a database works.
    python demo.py sample.sqlite3


This is the output:

..  code-block:: console

    $ python demo.py
    The requests module object:
    <module 'requests' (sample.sqlite3)>

    Requesting a webpage...success!

..  warning::

    The database format is likely to change as the project matures.


..  Links
..  -----
..
..  _the sqliteimport repository: https://github.com/kurtmckee/sqliteimport
