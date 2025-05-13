import pytest


def test_output_when_missing_cli_dependencies(capsys):
    with pytest.raises(SystemExit):
        import sqliteimport.cli  # noqa: F401  # imported by unused

    _, stderr = capsys.readouterr()
    assert "sqliteimport is not installed with CLI support" in stderr
