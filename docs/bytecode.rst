..
    This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
    Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT


Bytecode support
################

Python is able to import pre-compiled bytecode much, much faster than source code,
so sqliteimport supports pre-compiling and loading bytecode from databases.


Compiling bytecode
==================

The ``sqliteimport compile`` command compiles the Python source code to bytecode.

Because the bytecode format can change with each release of Python,
sqliteimport uses the Python interpreter's magic number to lock the bytecode
to the Python interpreter used to compile the bytecode.

For this reason, if ``sqliteimport compile`` is only run using CPython 3.13,
the bytecode in the database can only be used with CPython 3.13.
Other CPython versions will continue to import source code.
While reliable, it will be slow.
Therefore, ``sqliteimport compile`` should be run using additional CPython interpreters
that are supported by the application.

Cross-compiling bytecode example
--------------------------------

For example, if an application supports multiple interpreter versions
separate virtual environments could be created using different Python interpreters,
resulting in optimized imports for each supported Python interpreter.

The examples below show one possible way to accomplish this.

..  code-block:: shell-session
    :caption: Linux/macOS

    $ python3.13 -m venv venv-313
    $ venv-313/bin/pip install -r requirements.txt --target demo

    $ venv-313/bin/pip install sqliteimport[cli]
    $ venv-313/bin/sqliteimport bundle demo demo.sqlite3
    $ venv-313/bin/sqliteimport compile demo.sqlite3

    $ python3.12 -m venv venv-312
    $ venv-312/bin/pip install sqliteimport[cli]
    $ venv-312/bin/sqliteimport compile demo.sqlite3

..  code-block:: pwsh-session
    :caption: Windows (Powershell)

    > "C:\Program Files\Python313\python.exe" -m venv venv-313
    > venv-313\Scripts\pip install -r requirements.txt --target demo

    > venv-313\Scripts\pip install sqliteimport[cli]
    > venv-313\Scripts\sqliteimport bundle demo demo.sqlite3
    > venv-313\Scripts\sqliteimport compile demo.sqlite3

    > "C:\Program Files\Python312\python.exe" -m venv venv-312
    > venv-312\Scripts\pip install sqliteimport[cli]
    > venv-312\Scripts\sqliteimport compile demo.sqlite3


..  seealso::

    The CPython interpreter's source code contains `a list of magic numbers`_.


Loading bytecode
================

sqliteimport will always automatically load bytecode if available.
No additional configuration nor code is required.


..  Links
..  -----
..
.. _a list of magic numbers: https://github.com/python/cpython/blob/HEAD/Include/internal/pycore_magic_number.h
