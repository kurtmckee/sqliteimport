# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

python assets/performance clean
mkdir -p build/perfstats
python assets/performance generate -r custom-requirements.txt


# Filesystem -- source only
# -------------------------

Write-Host
Write-Host "filesystem / source"
python assets/performance run --importer filesystem --code-type source importsy.py


# Zip -- source only
# ------------------

Write-Host
Write-Host "zipimport / source"
$env:FILE_PREFIX="build\perfstats"
$env:OUTPUT_PATH="${env:FILE_PREFIX}\source.zip"
Compress-Archive -CompressionLevel Optimal -Path "build\perftest\*" -DestinationPath "${env:OUTPUT_PATH}"
python assets/performance run --importer zipimport --code-type source importsy.py



# Sqlite -- source only
# ---------------------

Write-Host
Write-Host "sqliteimport / source"
$env:FILE_PREFIX="build\perfstats"
$env:OUTPUT_PATH="${env:FILE_PREFIX}\source.sqlite3"
sqliteimport bundle "build\perftest" "${env:OUTPUT_PATH}" | Out-Null
python assets/performance run --importer sqliteimport --code-type source importsy.py


# Compile the source to bytecode
# ------------------------------

# Compile the source code to bytecode for each importer type.
python assets/performance compile --importer filesystem | Out-Null
python assets/performance compile --importer zipimport | Out-Null
python assets/performance compile --importer sqliteimport | Out-Null


# Filesystem -- bytecode
# ----------------------

Write-Host
Write-Host "filesystem / bytecode"
python assets/performance run --importer filesystem --code-type bytecode importsy.py


# Zip -- bytecode
# ---------------

# Delete the `__pycache__\` directories.
$cache_paths = Get-ChildItem -Recurse "build\perftest" | Where-Object { $_.Name -eq "__pycache__" }
Remove-Item -Recurse $cache_paths | Out-Null

Write-Host
Write-Host "zipimport / bytecode"
$env:FILE_PREFIX="build\perfstats"
$env:OUTPUT_PATH="${env:FILE_PREFIX}\bytecode.zip"
Compress-Archive -CompressionLevel Optimal -Path "build\perftest\*" -DestinationPath "${env:OUTPUT_PATH}"
python assets/performance run --importer zipimport --code-type bytecode importsy.py


# Sqlite -- bytecode
# ------------------

Write-Host
Write-Host "sqliteimport / bytecode"
python assets/performance run --importer sqliteimport --code-type bytecode importsy.py


# Capture the file sizes
# ----------------------

# Collect stats
# -------------

python assets/performance collect
python assets/performance plot --code-type source   --measurement time --output build/perfstats/windows-source-time.png
python assets/performance plot --code-type bytecode --measurement time --output build/perfstats/windows-bytecode-time.png
python assets/performance plot --code-type source   --measurement size --output build/perfstats/windows-source-size.png
python assets/performance plot --code-type bytecode --measurement size --output build/perfstats/windows-bytecode-size.png
