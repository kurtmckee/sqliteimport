import sqlite3

import sqliteimport


def test_load(monkeypatch):
    meta_path = []
    monkeypatch.setattr("sys.meta_path", meta_path)
    connection = sqlite3.connect(":memory:")
    sqliteimport.load(connection)
    connection.close()
    assert len(meta_path) == 1
