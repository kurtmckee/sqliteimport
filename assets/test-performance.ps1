# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

$env:PYTHONPROFILEIMPORTTIME=$null
$env:PYTHONDONTWRITEBYTECODE=1

Remove-Item -Recurse "build\perftest" | Out-Null
Remove-Item perf.* | Out-Null
python assets/generate-perftest-directory.py

# Note the size of the source code tree.
Write-Output "Source tree" > perf.files.log
Get-ChildItem -Recurse "build\perftest" | Measure-Object -Sum Length >> perf.files.log


$env:PYTHONPROFILEIMPORTTIME=1
$env:PYTHONDONTWRITEBYTECODE=1


# Filesystem -- source only
# -------------------------

Write-Host
$env:FILE_PREFIX="perf.filesystem.source"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="build\perftest"
Measure-Command {
    python -c 'import a; print(a)' 2>"${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"


# Zip -- source only
# ------------------

Write-Host
$env:FILE_PREFIX="perf.zip.source"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="${env:FILE_PREFIX}.zip"
Compress-Archive -CompressionLevel Optimal -Path "build\perftest\*" -DestinationPath "${env:PYTHONPATH}"
Measure-Command {
    python -c 'import a; print(a)' 2>"${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"



# Sqlite -- source only
# ---------------------

Write-Host
$env:FILE_PREFIX="perf.sqlite.source"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="${env:FILE_PREFIX}.sqlite3"
$env:PYTHONPROFILEIMPORTTIME=$null
sqliteimport bundle "build\perftest" "${env:PYTHONPATH}" | Out-Null
$env:PYTHONPROFILEIMPORTTIME=1
Measure-Command {
    python -c 'import sqliteimport; import a; print(a)' 2> "${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"


# Compile the source to bytecode
# ------------------------------

$env:PYTHONPROFILEIMPORTTIME=$null

# Compile into `__pycache__/` subdirectories for the filesystem.
python -m compileall -q "build\perftest"

# Note the size of the tree, including bytecode.
Write-Output "Source tree with bytecode" >> perf.files.log
Get-ChildItem -Recurse "build\perftest" | Measure-Object -Sum Length >> perf.files.log

# Compile in-place for zipimport.
python -m compileall -b -q "build\perftest"

$env:PYTHONPROFILEIMPORTTIME=1


# Filesystem -- bytecode
# ----------------------

Write-Host
$env:FILE_PREFIX="perf.filesystem.bytecode"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="build\perftest"
Measure-Command {
    python -c 'import a; print(a)' 2>"${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"


# Zip -- bytecode
# ---------------

# Delete the `__pycache__\` directories.
$cache_paths = Get-ChildItem -Recurse "build\perftest" | Where-Object { $_.Name -eq "__pycache__" }
Remove-Item -Recurse $cache_paths | Out-Null

Write-Host
$env:FILE_PREFIX="perf.zip.bytecode"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="${env:FILE_PREFIX}.zip"
Compress-Archive -CompressionLevel Optimal -Path "build\perftest\*" -DestinationPath "${env:PYTHONPATH}"
Measure-Command {
    python -c 'import a; print(a)' 2>"${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"


# Sqlite -- bytecode
# ------------------

Write-Host
$env:FILE_PREFIX="perf.sqlite.bytecode"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="${env:FILE_PREFIX}.sqlite3"
$env:PYTHONPROFILEIMPORTTIME=$null
sqliteimport bundle "build\perftest" "${env:PYTHONPATH}" | Out-Null
sqliteimport compile "${env:PYTHONPATH}"
$env:PYTHONPROFILEIMPORTTIME=1
Measure-Command {
    python -c 'import sqliteimport; import a; print(a)' 2> "${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"


# Capture the file sizes
# ----------------------

Get-ChildItem perf.*.zip,perf.*.sqlite3 >> perf.files.log
