Fixed
-----

*   Ensure that modules have a ``__file__`` attribute,
    and possibly a ``__cached__`` attribute.

    The Python data model docs make it clear that these attributes aren't guaranteed,
    but it is nevertheless common for authors to assume that ``__file__`` exists.

    The string value may not be usable for a specific purpose,
    but the attributes now exist with the correct type for increased compatibility.
