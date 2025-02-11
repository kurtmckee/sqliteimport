import json
import pathlib
import shutil
import subprocess
import sys


def main() -> int:
    root_directory = pathlib.Path(__file__).absolute().parent.parent

    filesystem_dist_directory = root_directory.parent / "dist/test-suite-filesystem"
    wipe_directory(filesystem_dist_directory)
    sqlite_dist_directory = root_directory.parent / "dist/test-suite-sqlite"
    wipe_directory(sqlite_dist_directory)

    tests_directory = root_directory / "tests"
    source_projects = tests_directory / "source-projects"
    for source_project in source_projects.glob("*/"):
        print(f"Regenerating {source_project.name}/filesystem...")
        build_wheel(source_project / "filesystem", filesystem_dist_directory)
        print(f"Regenerating {source_project.name}/sqlite...")
        build_wheel(source_project / "sqlite", sqlite_dist_directory)

    installed_projects = tests_directory / "installed-projects"
    wipe_directory(installed_projects)

    install_wheels(installed_projects / "filesystem", filesystem_dist_directory)
    install_wheels(installed_projects / "sqlite", sqlite_dist_directory)

    sanitize_dist_info_records(installed_projects)

    return 0


def wipe_directory(directory: pathlib.Path) -> None:
    """Erase the given directory and then re-create it."""

    if directory.exists():
        if not directory.is_dir():
            raise OSError(f"{directory} is not a directory.")
        shutil.rmtree(directory)

    directory.mkdir(parents=True, exist_ok=True)


def build_wheel(directory: pathlib.Path, output: pathlib.Path) -> None:
    """Build a wheel using Poetry."""

    command = f"{sys.executable} -m build --outdir={output} {directory}"
    run_command(command.split())


def install_wheels(target: pathlib.Path, dist_directory: pathlib.Path) -> None:
    """Install all wheels in the given directory."""

    # Install the wheels in the target directory.
    command = [
        *f"{sys.executable} -m pip install --target={target}".split(),
        *[str(path) for path in dist_directory.glob("*.whl")],
    ]
    run_command(command)


def sanitize_dist_info_records(directory: pathlib.Path) -> None:
    """Sanitize information in `.dist-info/` metadata directories.

    *   The `url` keys in "direct_url.json" files are modified.
        https://peps.python.org/pep-0610/

    *   The `direct_url.json` lines in "RECORD" files are modified.
        https://packaging.python.org/en/latest/specifications/recording-installed-packages/

    Modifying these files reduces unnecessary information entering version control.
    """

    # Modify `direct_url.json` files.
    for json_file in directory.rglob("**/*.dist-info/direct_url.json"):
        document = json.loads(json_file.read_text())
        if "url" in document:
            url = document["url"]
            if not url.startswith("file://"):
                raise ValueError(f"Unexpected URL value in {json_file}: {url}")
            document["url"] = f"file:///{pathlib.Path(url).name}"
            json_file.write_text(json.dumps(document))

    # Modify `RECORD` files.
    for record_file in directory.rglob("**/*.dist-info/RECORD"):
        with open(record_file) as file:
            lines = file.read().splitlines()
            newline = file.newlines
        output: list[str] = []
        for line in lines:
            if "__pycache__" in line:
                continue
            if ".dist-info/direct_url.json" in line:
                direct_url_json_path, _, _ = line.partition(",")
                line = f"{direct_url_json_path},,"
            output.append(line)
        record_file.write_text("\n".join(output), newline=newline)


def run_command(command: list[str]) -> None:
    try:
        subprocess.run(
            command,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        stdout = (error.stdout or b"<NONE>").decode("utf-8", errors="replace")
        stderr = (error.stderr or b"<NONE>").decode("utf-8", errors="replace")
        print("COMMAND")
        print("=======")
        print()
        print(" ".join(error.cmd))
        print()
        print()
        print("RETURN CODE")
        print("===========")
        print()
        print(error.returncode)
        print()
        print()
        print("STDOUT")
        print("======")
        print()
        print(stdout)
        print()
        print()
        print("STDERR")
        print("======")
        print()
        print(stderr)
        raise


if __name__ == "__main__":
    sys.exit(main())
