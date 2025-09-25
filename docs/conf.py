import pathlib
import tomllib

# General configuration
# ---------------------

# The suffix of source filenames.
source_suffix = ".rst"

# The main toctree document.
master_doc = "index"

# General information about the project.
project = "sqliteimport"
copyright = "2024-2025 Kurt McKee"

# Extract the project version.
pyproject_ = pathlib.Path(__file__).parent.parent / "pyproject.toml"
info_ = tomllib.loads(pyproject_.read_text())
version = release = info_["project"]["version"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Don't show "Powered by" text.
html_show_sphinx = False


# HTML theme configuration
# ------------------------

html_theme = "alabaster"
html_static_path = [
    "_static",
]
html_theme_options = {
    "logo": "logo.png",
    "logo_name": True,
    "description": "Import Python code from sqlite databases.",
    # Link to GitHub
    "github_user": "kurtmckee",
    "github_repo": "sqliteimport",
    "github_button": False,
    # Donation button
    "donate_url": "https://ko-fi.com/kurtmckee",
}
templates_path = ["_templates"]
html_sidebars = {
    "index": [
        "about-no-logo.html.jinja",  # Custom
        "donate.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
    ],
    "**": [
        "about.html.jinja",  # Custom
        "searchfield.html",
        "navigation.html",
        "relations.html",
        "donate.html",
    ],
}

# Don't copy source .rst files into the built documentation.
html_copy_source = False
