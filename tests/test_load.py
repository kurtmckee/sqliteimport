import sqlite3

import sqliteimport


def test_load(monkeypatch):
    meta_path = []
    monkeypatch.setattr("sys.meta_path", meta_path)
    sqliteimport.load(sqlite3.connect(":memory:"))
    assert len(meta_path) == 1
