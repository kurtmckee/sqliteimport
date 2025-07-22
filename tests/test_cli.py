# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import pytest


def test_output_when_missing_cli_dependencies(capsys):
    with pytest.raises(SystemExit):
        import sqliteimport.cli  # noqa: F401  # imported by unused

    _, stderr = capsys.readouterr()
    assert "sqliteimport is not installed with CLI support" in stderr
