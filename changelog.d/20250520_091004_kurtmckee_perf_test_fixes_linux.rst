Development
-----------

*   Fix performance testing issues, and capture more data, on Linux.

    Zip-based bytecode import times were skewed during testing
    because ``zipimport`` doesn't use PEP 3147 ``__pycache__/`` subdirectories.
    This is now accounted for by the performance testing script's setup steps,
    and zip-based import times are significantly more accurate.

    Also, the total size of the source code and byte code trees is captured.
