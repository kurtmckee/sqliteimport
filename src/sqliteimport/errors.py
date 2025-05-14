class SqliteImportError(Exception):
    pass


class FileNotFoundInDatabaseError(SqliteImportError, FileNotFoundError):
    def __init__(self, filename: str, database_path: str) -> None:
        super().__init__(
            2, "File not found in database", filename, None, database_path or ":memory:"
        )
