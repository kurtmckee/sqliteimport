# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import importlib
import os.path
import sys
import traceback

import pytest


@pytest.mark.parametrize(
    "package, separator",
    (
        ("package_filesystem", os.path.sep),
        ("package_sqlite", "/"),
    ),
)
def test_traceback(database, package, separator):
    """Ensure that tracebacks show lines from bundled source code."""

    module = importlib.import_module(f"{package}.zero_division")

    with pytest.raises(ZeroDivisionError) as error:
        module.trigger_zero_division_error()
    if sys.version_info >= (3, 10):
        formatted_exception = "".join(traceback.format_exception(error.value))
    else:
        # Python 3.9
        args = (type(error.value), error.value, error.value.__traceback__)
        formatted_exception = "".join(traceback.format_exception(*args))

    assert "<string>" not in formatted_exception
    assert f"{package}{separator}zero_division.py" in formatted_exception
    assert "1 / 0" in formatted_exception
