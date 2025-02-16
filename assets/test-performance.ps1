$env:PYTHONPROFILEIMPORTTIME=$null
$env:PYTHONDONTWRITEBYTECODE=1

Remove-Item -Recurse "build/perftest"
Remove-Item perf.*
python assets/generate-perftest-directory.py

$env:PYTHONPROFILEIMPORTTIME=1


# Filesystem -- source only
# -------------------------

Write-Host
$env:FILE_PREFIX="perf.filesystem.source"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="build/perftest"
Measure-Command {
    python -c 'import a; print(a)' 2>"${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"


# Zip -- source only
# ------------------

Write-Host
$env:FILE_PREFIX="perf.zip.source.storeonly"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="${env:FILE_PREFIX}.zip"
Compress-Archive -CompressionLevel NoCompression -Path "build\perftest\*" -DestinationPath "${env:PYTHONPATH}"
Measure-Command {
    python -c 'import a; print(a)' 2>"${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"

Write-Host
$env:FILE_PREFIX="perf.zip.source.fast"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="${env:FILE_PREFIX}.zip"
Compress-Archive -CompressionLevel Fastest -Path "build\perftest\*" -DestinationPath "${env:PYTHONPATH}"
Measure-Command {
    python -c 'import a; print(a)' 2>"${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"

Write-Host
$env:FILE_PREFIX="perf.zip.source.best"
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
python -m compileall -q "build/perftest"
$env:PYTHONPROFILEIMPORTTIME=1


# Filesystem -- bytecode
# ----------------------

Write-Host
$env:FILE_PREFIX="perf.filesystem.bytecode"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="build/perftest"
Measure-Command {
    python -c 'import a; print(a)' 2>"${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"


# Zip -- bytecode
# ---------------

Write-Host
$env:FILE_PREFIX="perf.zip.bytecode.storeonly"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="${env:FILE_PREFIX}.zip"
Compress-Archive -CompressionLevel NoCompression -Path "build\perftest\*" -DestinationPath "${env:PYTHONPATH}"
Measure-Command {
    python -c 'import a; print(a)' 2>"${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"

Write-Host
$env:FILE_PREFIX="perf.zip.bytecode.fast"
Write-Host "${env:FILE_PREFIX}"
$env:PYTHONPATH="${env:FILE_PREFIX}.zip"
Compress-Archive -CompressionLevel Fastest -Path "build\perftest\*" -DestinationPath "${env:PYTHONPATH}"
Measure-Command {
    python -c 'import a; print(a)' 2>"${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"

Write-Host
$env:FILE_PREFIX="perf.zip.bytecode.best"
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
$env:PYTHONPROFILEIMPORTTIME=1
Measure-Command {
    python -c 'import sqliteimport; import a; print(a)' 2> "${env:FILE_PREFIX}.import.log" | Write-Host
} > "${env:FILE_PREFIX}.time.log"


# Capture the file sizes
# ----------------------

Get-ChildItem perf.* > perf.files.log
