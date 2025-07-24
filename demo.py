# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import pathlib
import sys

import sqliteimport

if not len(sys.argv) == 2:
    print("A sqlite database must be provided as an argument.")
    sys.exit(1)
if not pathlib.Path(sys.argv[1]).is_file():
    print(f"{sys.argv[1]} must be an existing sqlite database.")
    print("Run 'python -m sqliteimport bundle' to get started.")
    sys.exit(1)

sqliteimport.load(sys.argv[1])

import requests  # noqa: E402

print("The requests module object:")
print(requests)

print()
print("Requesting a webpage...", end="")
requests.get("https://example.com/")
print("success!")
