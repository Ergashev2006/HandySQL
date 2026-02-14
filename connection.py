"""
easysql.connection
==================
Low-level connection management for SQLite, MySQL, and PostgreSQL.
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import Any, List, Tuple, Union

from .exceptions import DatabaseError, ConnectionError

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import psycopg2
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

logger = logging.getLogger(__name__)


class Connection:
    """
    Manages a single database connection.

    Parameters
    ----------
    db_type : str
        ``"sqlite"``, ``"mysql"``, or ``"postgresql"``
    **kwargs
        Connection parameters (host, user, password, database, port …)
    """

    _ID_TYPES = {
        "sqlite":     "INTEGER PRIMARY KEY AUTOINCREMENT",
        "mysql":      "INT AUTO_INCREMENT PRIMARY KEY",
        "postgresql": "SERIAL PRIMARY KEY",
    }

    def __init__(self, db_type: str = "sqlite", **kwargs):
        self.db_type = db_type.lower()
        self._conn   = None
        self._auto_commit = kwargs.pop("auto_commit", True)
        self._params = kwargs

        if self.db_type == "sqlite":
            self._db_path = kwargs.get("database", ":memory:")
        elif self.db_type == "mysql":
            if not MYSQL_AVAILABLE:
                raise ConnectionError(
                    "mysql-connector-python is not installed.\n"
                    "Run: pip install mysql-connector-python"
                )
        elif self.db_type == "postgresql":
            if not POSTGRESQL_AVAILABLE:
                raise ConnectionError(
                    "psycopg2 is not installed.\n"
                    "Run: pip install psycopg2-binary"
                )
        else:
            raise DatabaseError(
                f"Unsupported database type: '{db_type}'. "
                "Choose 'sqlite', 'mysql', or 'postgresql'."
            )

    # ------------------------------------------------------------------ #

    def open(self):
        """Open (or return existing) database connection."""
        if self._conn is not None:
            return self._conn
        try:
            p = self._params
            if self.db_type == "sqlite":
                self._conn = sqlite3.connect(self._db_path)
                self._conn.row_factory = sqlite3.Row
                logger.info("SQLite connected: %s", self._db_path)
            elif self.db_type == "mysql":
                self._conn = mysql.connector.connect(
                    host=p.get("host", "localhost"),
                    user=p.get("user", "root"),
                    password=p.get("password", ""),
                    database=p.get("database", ""),
                    port=p.get("port", 3306),
                )
                logger.info("MySQL connected: %s", p.get("database"))
            elif self.db_type == "postgresql":
                self._conn = psycopg2.connect(
                    host=p.get("host", "localhost"),
                    user=p.get("user", "postgres"),
                    password=p.get("password", ""),
                    database=p.get("database", ""),
                    port=p.get("port", 5432),
                )
                logger.info("PostgreSQL connected: %s", p.get("database"))
            return self._conn
        except Exception as exc:
            raise ConnectionError(f"Connection failed: {exc}") from exc

    def close(self):
        """Close the connection if open."""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("Connection closed")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.close()

    # ------------------------------------------------------------------ #

    @contextmanager
    def cursor(self):
        """Context manager that yields a cursor and handles commit/rollback."""
        if self._conn is None:
            self.open()
        cur = self._conn.cursor()
        try:
            yield cur
            if self._auto_commit:
                self._conn.commit()
        except Exception as exc:
            self._conn.rollback()
            logger.error("Rolled back: %s", exc)
            raise DatabaseError(f"Database operation error: {exc}") from exc
        finally:
            cur.close()

    # ------------------------------------------------------------------ #

    def execute(self, sql: str, params: Union[Tuple, List] = None) -> Any:
        """
        Run a SQL statement.

        Returns
        -------
        list[dict]  for SELECT
        int         (rowcount) for INSERT / UPDATE / DELETE
        """
        with self.cursor() as cur:
            logger.debug("SQL: %s | params: %s", sql, params)
            cur.execute(sql, params or ())
            if sql.strip().upper().startswith("SELECT"):
                rows = cur.fetchall()
                if self.db_type == "sqlite":
                    return [dict(r) for r in rows]
                cols = [c[0] for c in cur.description]
                return [dict(zip(cols, r)) for r in rows]
            return cur.rowcount

    def execute_many(self, sql: str, params_list: List[Tuple]) -> int:
        """Run a parameterised statement for each item in params_list."""
        with self.cursor() as cur:
            cur.executemany(sql, params_list)
            return cur.rowcount

    # ------------------------------------------------------------------ #
    #  Transaction helpers
    # ------------------------------------------------------------------ #

    def begin(self):
        """Disable auto-commit to start a manual transaction."""
        if self._conn is None:
            self.open()
        self._auto_commit = False
        logger.info("Transaction started")

    def commit(self):
        """Commit the current transaction."""
        if self._conn:
            self._conn.commit()
            logger.info("Transaction committed")

    def rollback(self):
        """Roll back the current transaction."""
        if self._conn:
            self._conn.rollback()
            logger.info("Transaction rolled back")

    # ------------------------------------------------------------------ #

    @property
    def auto_id_sql(self) -> str:
        """Return the correct auto-increment primary key definition."""
        return self._ID_TYPES[self.db_type]
