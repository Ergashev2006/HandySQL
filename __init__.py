"""
HandySQL
=======
A simple and powerful SQL library for Python.

Supported databases: SQLite · MySQL · PostgreSQL

Quick start
-----------
>>> from HandySQL import HandySQL
>>>
>>> with HandySQL(db_type="sqlite", database="app.db") as db:
...     db.quick_table("users", "name", "email")
...     db.add("users", name="Alice", email="alice@example.com")
...     users = db.get_all("users")

Public API
----------
Classes:
    HandySQL        – main database interface
    SQLBuilder     – fluent SQL query builder
    DatabaseError  – library exception

Functions:
    create_connection(db_type, **kwargs) -> HandySQL
    sql_builder(table)                   -> SQLBuilder
"""

from .sql_easy import (
    HandySQL,
    SQLBuilder,
    DatabaseError,
    create_connection,
    sql_builder,
    MYSQL_AVAILABLE,
    POSTGRESQL_AVAILABLE,
)

__all__ = [
    "HandySQL",
    "SQLBuilder",
    "DatabaseError",
    "create_connection",
    "sql_builder",
    "MYSQL_AVAILABLE",
    "POSTGRESQL_AVAILABLE",
]

__version__   = "1.0.0"
__author__    = "HandySQL Team"
__license__   = "MIT"
__url__       = "https://github.com/HandySQL/HandySQL"
