Fixed
-----

*   Fix a bug in the bundling code that allowed non-Python files to be importable.

    Previously, a package containing a PEP 561 ``py.typed`` file
    would have an importable submodule named ``{package}.py``.
