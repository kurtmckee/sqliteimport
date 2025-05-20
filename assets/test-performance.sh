#!/usr/bin/env sh
# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

set -eu

rm -rf "build/perftest" || true
rm perf.* || true
python assets/generate-perftest-directory.py

# Note the size of the source code tree.
echo "Source tree" > perf.files.log
du --max-depth=0 --bytes build/perftest >> perf.files.log


export PYTHONPROFILEIMPORTTIME=1
export PYTHONDONTWRITEBYTECODE=1


# Filesystem -- source only
# -------------------------

echo
export FILE_PREFIX="perf.filesystem.source"
echo "${FILE_PREFIX}"
export PYTHONPATH="build/perftest"
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import a; print(a)' 2> "${FILE_PREFIX}.import.log"


# Zip -- source only
# ------------------

echo
export FILE_PREFIX="perf.zip.source"
echo "${FILE_PREFIX}"
export PYTHONPATH="${FILE_PREFIX}.zip"
cd "build/perftest"
zip -qr9 "../../${PYTHONPATH}" .
cd "../.."
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import a; print(a)' 2> "${FILE_PREFIX}.import.log"


# Sqlite -- source only
# ---------------------

echo
export FILE_PREFIX="perf.sqlite.source"
echo "${FILE_PREFIX}"
export PYTHONPATH="${FILE_PREFIX}.sqlite3"
PYTHONPROFILEIMPORTTIME="" sqliteimport bundle "build/perftest" "${PYTHONPATH}" 1>/dev/null
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import sqliteimport; import a; print(a)' 2> "${FILE_PREFIX}.import.log"


# Compile the source to bytecode
# ------------------------------

# Compile into `__pycache__/` subdirectories for the filesystem.
PYTHONPROFILEIMPORTTIME="" python -m compileall -q "build/perftest"

# Note the size of the tree, including bytecode.
echo "Source tree with bytecode" >> perf.files.log
du --max-depth=0 --bytes build/perftest >> perf.files.log

# Compile in-place for zipimport.
PYTHONPROFILEIMPORTTIME="" python -m compileall -b -q "build/perftest"


# Filesystem -- bytecode
# ----------------------

echo
export FILE_PREFIX="perf.filesystem.bytecode"
echo "${FILE_PREFIX}"
export PYTHONPATH="build/perftest"
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import a; print(a)' 2> "${FILE_PREFIX}.import.log"


# Zip -- bytecode
# ---------------

echo
export FILE_PREFIX="perf.zip.bytecode"
echo "${FILE_PREFIX}"
export PYTHONPATH="${FILE_PREFIX}.zip"
cd "build/perftest"
zip -qr9 "../../${PYTHONPATH}" . --exclude '*/__pycache__/*'
cd "../.."
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import a; print(a)' 2> "${FILE_PREFIX}.import.log"


# Sqlite -- bytecode
# ------------------

echo
export FILE_PREFIX="perf.sqlite.bytecode"
echo "${FILE_PREFIX}"
export PYTHONPATH="${FILE_PREFIX}.sqlite3"
PYTHONPROFILEIMPORTTIME="" sqliteimport bundle "build/perftest" "${PYTHONPATH}" 1>/dev/null
PYTHONPROFILEIMPORTTIME="" sqliteimport compile "${PYTHONPATH}"
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import sqliteimport; import a; print(a)' 2> "${FILE_PREFIX}.import.log"


# Capture the file sizes
# ----------------------

ls -l perf.*.zip perf.*.sqlite3 >> perf.files.log
