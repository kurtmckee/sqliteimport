Added
-----

*   Support compiling to, and loading from, pre-compiled bytecode in the database.

    Performance testing on Linux shows that sqliteimport is now faster
    than the filesystem when loading large dependency trees.

*   Add a ``sqliteimport compile`` command to compile all Python source to bytecode.

    The command should be run for each Python interpreter that will be used
    by the application.
