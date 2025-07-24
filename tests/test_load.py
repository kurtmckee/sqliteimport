# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import sqlite3

import sqliteimport


def test_load(monkeypatch):
    meta_path = []
    monkeypatch.setattr("sys.meta_path", meta_path)
    connection = sqlite3.connect(":memory:")
    sqliteimport.load(connection)
    connection.close()
    assert len(meta_path) == 1
