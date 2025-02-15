Added
-----

*   Add initial support for bundling and loading Python bytecode (``.pyc`` files).

    Performance testing on Linux shows that loading from sqlite is now twice as fast.

    The implementation currently binds the sqlite database
    to the Python version used to bundle it.
