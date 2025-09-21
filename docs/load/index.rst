..
    This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
    Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT


Loading sqliteimport
####################

sqliteimport must be imported and configured
before packages stored in sqlite can be imported.
There are two considerations:

#.  When and where sqliteimport is *imported*
#.  How the path to the sqlite database is *configured*

Table of contents
=================

*   :ref:`automatic`
*   :ref:`manual-import`
*   :ref:`manual-load`


..  _automatic:

Automatic everything
====================

The simplest way to import sqliteimport and configure a database of packages
is to create a custom ``sitecustomize`` module
and set the ``PYTHONPATH`` environment variable.

This technique allows a database of packages to be used
*without modifying any application code*.

..  code-block:: python
    :caption: ``sitecustomize.py``

    import sqliteimport

..  code-block:: bash
    :caption: Linux/macOS

    export PYTHONPATH='path/to/packages.sqlite3'

..  code-block:: powershell
    :caption: Windows Powershell

    $env:PYTHONPATH='path/to/packages.sqlite3'

..  note::

    ``sitecustomize.py`` must be in a directory that Python's ``site`` module
    automatically searches.
    Please read the `Python site module`_ documentation for full details.

..  warning::

    This technique may fail under some circumstances.

    For example, Python interpreters installed by Homebrew
    include a custom ``sitecustomize`` that will be found and used
    before any that are created in a virtual environment.


Examples
--------

The examples below demonstrate how to use a ``sitecustomize.py`` file
with a ``PYTHONPATH`` environment variable.

..  literalinclude:: assets/automatic.sh
    :caption: Linux/macOS
    :language: bash
    :lines: 2-

..  literalinclude:: assets/automatic.ps1
    :caption: Windows Powershell
    :language: powershell



..  _manual-import:

Manual imports
==============

In some circumstances it may be helpful, or even necessary,
to import sqliteimport in your application code.
The obvious requirement is that sqliteimport must be imported
before any packages that are bundled in a sqlite database.

Linters that sort Python imports may move ``import sqliteimport``
and prevent your code from executing.
See the :doc:`../isort/index` and :doc:`../ruff/index` pages
for suggestions how to configure those linters.


..  _manual-load:

Manual database loading
=======================

If you cannot configure or control the ``PYTHONPATH`` environment variable
to point to a sqlite database, you'll need to load a database manually.

This is accomplished by calling ``sqliteimport.load()`` with a path
to the database, represented as either a string or ``pathlib.Path`` instance.

..  code-block:: python

    import sqliteimport

    sqliteimport.load("path/to/packages.sqlite3")

    import example_package_from_database


..  Links
..  -----
..
..  _Python site module: https://docs.python.org/3/library/site.html
