#!/usr/bin/env bash
# Install sqliteimport in a virtual environment.
python -m venv demo-venv
source demo-venv/bin/activate
python -m pip install sqliteimport[cli]

# Install flake8 and bundle it into a database.
python -m pip install flake8 --target flake8/
sqliteimport bundle flake8/ flake8.sqlite3
rm -rf flake8/

# Create a `sitecustomize.py` file.
site_packages_directory="$(python -c 'import site; print(site.getsitepackages()[0])')"
echo "Creating a sitecustomize.py file in ${site_packages_directory}"
echo 'import sqliteimport' > "${site_packages_directory}/sitecustomize.py"

# Point PYTHONPATH at the database.
export PYTHONPATH="flake8.sqlite3"

# Run flake8, and show where it's imported from.
python -m flake8 --version
python -c 'import flake8; print(f"Imported flake8 from {flake8.__file__!r}")'
