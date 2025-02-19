# This file is a part of sqliteimport <https://github.com/kurtmckee/sqliteimport>
# Copyright 2024-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from .accessor import Accessor
from .compat import marshal
from .util import get_magic_number


def compile_bytecode(accessor: Accessor) -> None:
    """Compile source code already in the database."""

    magic_number = get_magic_number()
    if magic_number in accessor.get_magic_numbers():
        return

    accessor.create_bytecode_table(magic_number)
    for row in accessor.iter_source_code():
        fullname, path, is_package, source = row
        code = compile(source, filename=path, mode="exec", dont_inherit=True)
        bytecode = marshal.dumps(code, allow_code=True)
        accessor.add_bytecode(magic_number, fullname, path, is_package, bytecode)

    accessor.mark_magic_number(magic_number)
