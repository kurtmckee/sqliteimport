# generate-sample.py must be run prior to running this demo.

import sqliteimport

sqliteimport.load("sample.sqlite3")


import requests  # noqa: E402

print("The requests module object:")
print(requests)

print()
print("Requesting a webpage...", end="")
requests.get("https://example.com/")
print("success!")
