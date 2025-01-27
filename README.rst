..
    This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
    Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT


..  image:: https://raw.githubusercontent.com/kurtmckee/sqliteimport/dfd7095f2df8d6e9249889dd85f102027d1a6cfb/docs/_static/banner.png
    :alt: sqlite import: Import Python code in sqlite databases.

-------------------------------------------------------------------------------

Demo usage example, using ``demo.py`` in `the sqliteimport repository`_:

..  code-block:: bash

    # Ensure sqliteimport is installed with the 'cli' extra.
    pip install sqliteimport[cli]

    # Install 'requests' in a standalone directory.
    pip install --target=sample requests

    # Generate a sqlite database containing the installed packages.
    sqliteimport bundle sample sample.sqlite3

    # Demonstrate that importing from a database works.
    python demo.py sample.sqlite3


This is the output:

..  code-block:: console

    $ python demo.py
    The requests module object:
    <module 'requests' (sample.sqlite3)>

    Requesting a webpage...success!

..  warning::

    The database format is likely to change as the project matures.


Attributions
============

The sqliteimport logo and banner build on others' work.

*   The package in the logo is `Emoji 1F4E6`_
    and is designed by `OpenMoji`_, the open-source emoji and icon project.

    License: `CC BY-SA 4.0`_

*   The feather in the logo is `Emoji 1FAB6`_
    and is designed by `OpenMoji`_, the open-source emoji and icon project.

    License: `CC BY-SA 4.0`_

*   The phrase "sqlite import" in the banner uses the `Dancing Script v2.031`_ font,
    designed by `Pablo Impallari <Dancing Script author_>`_.

    License: `SIL Open Font License, v1.1 <Dancing Script license_>`_

*   The phrase "Import Python code from sqlite databases" in the banner uses the `Noto Sans`_ font,
    designed by the `Noto Project`_.

    License: `SIL Open Font License, version 1.1 <Noto Sans License_>`_

*   The logo and banner were pieced together using `Inkscape`_.

    License: `GNU GPL, version 2`_


..  Links
..  -----
..
..  _the sqliteimport repository: https://github.com/kurtmckee/sqliteimport
..  _Emoji 1F4E6: https://openmoji.org/library/emoji-1F4E6/
..  _Emoji 1FAB6: https://openmoji.org/library/emoji-1FAB6/
..  _OpenMoji: https://openmoji.org/
..  _CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/
..  _Dancing Script v2.031: https://github.com/impallari/DancingScript/tree/7f1738a1e8034404b1985c442af480155c603955/fonts/v2031
..  _Dancing Script license: https://github.com/impallari/DancingScript/blob/7f1738a1e8034404b1985c442af480155c603955/OFL.txt
..  _Dancing Script author: https://github.com/impallari
..  _Noto Sans: https://fonts.google.com/noto/specimen/Noto+Sans
..  _Noto Project: https://github.com/notofonts/latin-greek-cyrillic
..  _Noto Sans License: https://github.com/notofonts/latin-greek-cyrillic/blob/4bc63d7ebca1faed49c6c685f380ba0abc2c1941/OFL.txt
..  _Inkscape: https://inkscape.org/
..  _GNU GPL, version 2: https://inkscape.org/about/license/
