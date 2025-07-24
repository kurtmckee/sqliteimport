#!/usr/bin/env sh

# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

set -eu

python assets/performance clean
mkdir -p build/perfstats
python assets/performance generate -r custom-requirements.txt


# Filesystem -- source only
# -------------------------

echo
echo filesystem / source
python assets/performance run --importer filesystem --code-type source importsy.py


# Zip -- source only
# ------------------

echo
export FILE_PREFIX="build/perfstats"
echo "zipimport / source"
export PYTHONPATH="${FILE_PREFIX}/source.zip"
cd "build/perftest"
zip -qr9 "../../${PYTHONPATH}" .
cd "../.."
python assets/performance run --importer zipimport --code-type source importsy.py


# Sqlite -- source only
# ---------------------

echo
export FILE_PREFIX="build/perfstats"
echo "sqliteimport / source"
export PYTHONPATH="${FILE_PREFIX}/source.sqlite3"
sqliteimport bundle "build/perftest" "${PYTHONPATH}" 1>/dev/null
python assets/performance run --importer sqliteimport --code-type source importsy.py


# Compile the source to bytecode
# ------------------------------

# Compile the source code to bytecode for each importer type.
python assets/performance compile --importer filesystem 1>/dev/null
python assets/performance compile --importer zipimport 1>/dev/null
python assets/performance compile --importer sqliteimport 1>/dev/null


# Filesystem -- bytecode
# ----------------------

echo
echo "filesystem / bytecode"
python assets/performance run --importer filesystem --code-type bytecode importsy.py


# Zip -- bytecode
# ---------------

echo
export FILE_PREFIX="build/perfstats"
echo "zipimport / bytecode"
export PYTHONPATH="${FILE_PREFIX}/bytecode.zip"
cd "build/perftest"
zip -qr9 "../../${PYTHONPATH}" . --exclude '*/__pycache__/*'
cd "../.."
python assets/performance run --importer zipimport --code-type bytecode importsy.py


# Sqlite -- bytecode
# ------------------

echo
echo "sqliteimport / bytecode"
python assets/performance run --importer sqliteimport --code-type bytecode importsy.py


# Collect stats
# -------------

python assets/performance collect
python assets/performance plot --code-type source   --measurement time --output build/perfstats/linux-source-time.png
python assets/performance plot --code-type bytecode --measurement time --output build/perfstats/linux-bytecode-time.png
python assets/performance plot --code-type source   --measurement size --output build/perfstats/linux-source-size.png
python assets/performance plot --code-type bytecode --measurement size --output build/perfstats/linux-bytecode-size.png
