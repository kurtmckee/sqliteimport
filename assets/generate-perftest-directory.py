# Generate a directory suitable for performance testing.

import pathlib
import sys

print("This will generate ~1,300 files and consume ~1.2GB of disk space.")
if input("Continue [y/N]? ").lower().strip()[:1] != "y":
    sys.exit(1)


DEPTH = 50
LETTERS = "bcdefghijklmnopqrstuvwxyz"  # 'a' is deliberately skipped.

root = pathlib.Path(__file__).parent.parent / "build/perftest"
root.mkdir(exist_ok=True)
path = root / "/".join("a" for i in range(DEPTH))
path.mkdir(parents=True, exist_ok=True)

# Create a deep and wide chain of imports.
first_line = "from . import a"
other_lines = [f"from . import {letter}" for letter in LETTERS]

code = "\n".join(["#" * 100 for number in range(10_000)])


current_path = path
while current_path != root:
    print(current_path)
    (current_path / "__init__.py").write_text("\n".join([first_line] + other_lines))
    for letter in LETTERS:
        (current_path / f"{letter}.py").write_text(code)
    current_path = current_path.parent

# Overwrite the deepest __init__.py.
(path / "__init__.py").write_text("\n".join([f"depth = {DEPTH}"] + other_lines))
