"""
easysql.exceptions
==================
All exceptions raised by the EasySQL library.
"""


class DatabaseError(Exception):
    """
    Raised for any EasySQL / database-level error.

    Examples
    --------
    >>> from easysql import DatabaseError
    >>> try:
    ...     db.remove("users")          # missing filter
    ... except DatabaseError as e:
    ...     print(f"Caught: {e}")
    """
    pass


class ConnectionError(DatabaseError):
    """Raised when a connection to the database cannot be established."""
    pass


class TableNotFoundError(DatabaseError):
    """Raised when an operation targets a table that does not exist."""
    pass


class RecordNotFoundError(DatabaseError):
    """Raised when a required row is not found (e.g. clone_row with bad ID)."""
    pass


class ValidationError(DatabaseError):
    """Raised when input data fails a safety check (e.g. empty filter on delete)."""
    pass
