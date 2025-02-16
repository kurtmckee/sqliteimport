#!/usr/bin/env sh

set -eu

rm -rf "build/perftest" || true
rm perf.* || true
python assets/generate-perftest-directory.py

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
export FILE_PREFIX="perf.zip.source.storeonly"
echo "${FILE_PREFIX}"
export PYTHONPATH="${FILE_PREFIX}.zip"
cd "build/perftest"
zip -qr0 "../../${PYTHONPATH}" .
cd "../.."
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import a; print(a)' 2> "${FILE_PREFIX}.import.log"

echo
export FILE_PREFIX="perf.zip.source.fast"
echo "${FILE_PREFIX}"
export PYTHONPATH="${FILE_PREFIX}.zip"
cd "build/perftest"
zip -qr1 "../../${PYTHONPATH}" .
cd "../.."
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import a; print(a)' 2> "${FILE_PREFIX}.import.log"

echo
export FILE_PREFIX="perf.zip.source.best"
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

PYTHONPROFILEIMPORTTIME="" python -m compileall -q "build/perftest"


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
export FILE_PREFIX="perf.zip.bytecode.storeonly"
echo "${FILE_PREFIX}"
export PYTHONPATH="${FILE_PREFIX}.zip"
cd "build/perftest"
zip -qr0 "../../${PYTHONPATH}" .
cd "../.."
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import a; print(a)' 2> "${FILE_PREFIX}.import.log"

echo
export FILE_PREFIX="perf.zip.bytecode.fast"
echo "${FILE_PREFIX}"
export PYTHONPATH="${FILE_PREFIX}.zip"
cd "build/perftest"
zip -qr1 "../../${PYTHONPATH}" .
cd "../.."
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import a; print(a)' 2> "${FILE_PREFIX}.import.log"

echo
export FILE_PREFIX="perf.zip.bytecode.best"
echo "${FILE_PREFIX}"
export PYTHONPATH="${FILE_PREFIX}.zip"
cd "build/perftest"
zip -qr9 "../../${PYTHONPATH}" .
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
command time --portability --output "${FILE_PREFIX}.time.log" \
    python -c 'import sqliteimport; import a; print(a)' 2> "${FILE_PREFIX}.import.log"


# Capture the file sizes
# ----------------------

ls -l perf.* > perf.files.log
