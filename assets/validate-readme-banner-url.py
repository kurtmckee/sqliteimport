# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

"""
Validate that the banner image in the README points to its most recent update.

This helps ensure that each release on PyPI renders the README in a predictable way.
"""

import subprocess
import sys

BANNER = "docs/_static/banner.png"
GET_LATEST_BANNER_SHA = f"git rev-list --max-count=1 HEAD {BANNER}"

try:
    stdout = subprocess.check_output(GET_LATEST_BANNER_SHA.split())
except subprocess.CalledProcessError:
    print("There was an error getting the latest commit SHA that changed the banner")
    sys.exit(1)

try:
    sha = stdout.strip().decode("utf-8")
except UnicodeError:
    print("There was an error decoding the 'git rev-parse' output")
    sys.exit(1)

with open("README.rst") as file:
    readme = file.read()

if f"{sha}/{BANNER}" not in readme:
    print("The latest commit that changed the banner isn't in the README.")
    print("Modify the README to include this image URL:")
    print()
    print(f"https://raw.githubusercontent.com/kurtmckee/sqliteimport/{sha}/{BANNER}")
    print()
    sys.exit(1)
