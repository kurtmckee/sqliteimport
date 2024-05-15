import pathlib
import sqlite3

database_file = "sample.sqlite3"
pathlib.Path(database_file).unlink(missing_ok=True)

conn = sqlite3.connect(database_file)
conn.execute(
    """
    CREATE TABLE code (
        fullname text,
        path text,
        is_package boolean,
        source text
    );
"""
)

root = pathlib.Path("sample")

paths: list[pathlib.Path] = list(root.glob("*"))
files = []
for path in paths:
    rel_path = path.relative_to(root)
    if rel_path.suffix in (".dist-info", ".so"):
        continue
    if rel_path.name == "__pycache__":
        continue
    if str(rel_path) == "bin":
        continue
    if path.is_dir():
        files.append((rel_path, (path / "__init__.py").exists()))
        paths.extend(path.glob("*"))
    else:
        files.append((rel_path, False))

for file, is_package in sorted(files):
    print(f"{'* ' if is_package else '  '} {file}")
    if (root / file).is_dir():
        continue
    fullname = file.parent if file.name == "__init__.py" else file.with_suffix("")
    is_package = file.name == "__init__.py"
    conn.execute(
        "INSERT INTO code (fullname, path, is_package, source) VALUES (?, ?, ?, ?);",
        (
            str(fullname).replace("/", ".").replace("\\", "."),
            str(file),
            is_package,
            (root / file).read_text(),
        ),
    ).fetchone()

conn.commit()
conn.close()
