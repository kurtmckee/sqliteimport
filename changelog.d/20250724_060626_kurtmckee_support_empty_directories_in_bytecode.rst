Fixed
-----

*   Fall back to importing from source code if importing from byte code fails.

    This resolves a problem importing Flask when byte-compiled,
    due to its ``sansio`` subdirectory, which has no ``__init__.py`` file
    and whose submodules currently fail to import from the byte code table.
