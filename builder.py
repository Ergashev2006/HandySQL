"""
easysql.builder
===============
Fluent SQL query builder.

Usage
-----
>>> from easysql import sql_builder
>>>
>>> q = (sql_builder("users")
...         .select(["name", "email"])
...         .where("age > ?", 18)
...         .order_by("name")
...         .limit(10))
>>> sql, params = q.build()
"""

from typing import Any, List, Tuple, Union
from .exceptions import DatabaseError


class SQLBuilder:
    """
    Fluent builder for SELECT / INSERT / UPDATE / DELETE statements.

    Every method returns ``self``, so calls can be chained::

        builder = (SQLBuilder("users")
                    .select("*")
                    .where("age > ?", 18)
                    .order_by("name", "ASC")
                    .limit(10))
        sql, params = builder.build()
    """

    def __init__(self, table: str = None):
        self.table          = table
        self._select        = "*"
        self._where         = []
        self._where_params  = []
        self._order_by      = None
        self._limit         = None
        self._offset        = None
        self._join          = []
        self._set_values    = {}
        self._insert_values = []
        self._operation     = None
        self._group_by      = None
        self._having        = None
        self._distinct      = False

    # ------------------------------------------------------------------ #
    #  SELECT helpers
    # ------------------------------------------------------------------ #

    def select(self, columns: Union[str, List[str]] = "*") -> "SQLBuilder":
        """Set the SELECT column list."""
        self._operation = "SELECT"
        self._select = ", ".join(columns) if isinstance(columns, list) else columns
        return self

    def distinct(self) -> "SQLBuilder":
        """Add the DISTINCT keyword."""
        self._distinct = True
        return self

    # ------------------------------------------------------------------ #
    #  WHERE / AND / OR
    # ------------------------------------------------------------------ #

    def where(self, condition: str, *params) -> "SQLBuilder":
        """
        Add a WHERE condition.
        Automatically prepends AND when a condition already exists.
        """
        if self._where:
            self._where.append(f"AND {condition}")
        else:
            self._where.append(condition)
        self._where_params.extend(params)
        return self

    def and_where(self, condition: str, *params) -> "SQLBuilder":
        """Explicitly add an AND condition (alias for where())."""
        return self.where(condition, *params)

    def or_where(self, condition: str, *params) -> "SQLBuilder":
        """Add an OR condition."""
        if self._where:
            self._where.append(f"OR {condition}")
        else:
            self._where.append(condition)
        self._where_params.extend(params)
        return self

    def where_in(self, column: str, values: List[Any]) -> "SQLBuilder":
        """Add a WHERE … IN (…) condition."""
        placeholders = ", ".join("?" for _ in values)
        self._where.append(
            f"AND {column} IN ({placeholders})" if self._where
            else f"{column} IN ({placeholders})"
        )
        self._where_params.extend(values)
        return self

    def where_between(self, column: str, start: Any, end: Any) -> "SQLBuilder":
        """Add a WHERE … BETWEEN … AND … condition."""
        prefix = "AND " if self._where else ""
        self._where.append(f"{prefix}{column} BETWEEN ? AND ?")
        self._where_params.extend([start, end])
        return self

    def where_like(self, column: str, pattern: str) -> "SQLBuilder":
        """Add a WHERE … LIKE … condition."""
        prefix = "AND " if self._where else ""
        self._where.append(f"{prefix}{column} LIKE ?")
        self._where_params.append(pattern)
        return self

    def where_null(self, column: str, is_null: bool = True) -> "SQLBuilder":
        """Add WHERE … IS NULL or IS NOT NULL."""
        prefix = "AND " if self._where else ""
        qualifier = "IS NULL" if is_null else "IS NOT NULL"
        self._where.append(f"{prefix}{column} {qualifier}")
        return self

    # ------------------------------------------------------------------ #
    #  Ordering / grouping / paging
    # ------------------------------------------------------------------ #

    def order_by(self, column: str, direction: str = "ASC") -> "SQLBuilder":
        """Set ORDER BY clause."""
        self._order_by = f"{column} {direction}".strip()
        return self

    def group_by(self, columns: Union[str, List[str]]) -> "SQLBuilder":
        """Set GROUP BY clause."""
        self._group_by = ", ".join(columns) if isinstance(columns, list) else columns
        return self

    def having(self, condition: str) -> "SQLBuilder":
        """Set HAVING clause."""
        self._having = condition
        return self

    def limit(self, n: int) -> "SQLBuilder":
        """Set LIMIT."""
        self._limit = n
        return self

    def offset(self, n: int) -> "SQLBuilder":
        """Set OFFSET."""
        self._offset = n
        return self

    # ------------------------------------------------------------------ #
    #  JOINs
    # ------------------------------------------------------------------ #

    def join(self, table: str, on: str, join_type: str = "INNER") -> "SQLBuilder":
        """Add a JOIN clause."""
        self._join.append(f"{join_type} JOIN {table} ON {on}")
        return self

    def left_join(self, table: str, on: str) -> "SQLBuilder":
        """Shorthand for LEFT JOIN."""
        return self.join(table, on, "LEFT")

    def right_join(self, table: str, on: str) -> "SQLBuilder":
        """Shorthand for RIGHT JOIN."""
        return self.join(table, on, "RIGHT")

    # ------------------------------------------------------------------ #
    #  DML starters
    # ------------------------------------------------------------------ #

    def insert(self, table: str) -> "SQLBuilder":
        """Start an INSERT statement."""
        self._operation = "INSERT"
        self.table = table
        return self

    def values(self, **kwargs) -> "SQLBuilder":
        """Provide a row dict for INSERT."""
        self._insert_values.append(kwargs)
        return self

    def update(self, table: str) -> "SQLBuilder":
        """Start an UPDATE statement."""
        self._operation = "UPDATE"
        self.table = table
        return self

    def set(self, **kwargs) -> "SQLBuilder":
        """Provide SET values for UPDATE."""
        self._set_values.update(kwargs)
        return self

    def delete(self, table: str) -> "SQLBuilder":
        """Start a DELETE statement."""
        self._operation = "DELETE"
        self.table = table
        return self

    # ------------------------------------------------------------------ #
    #  Build
    # ------------------------------------------------------------------ #

    def build(self) -> Tuple[str, List[Any]]:
        """
        Compile the builder into ``(sql_string, params_list)``.

        Raises
        ------
        DatabaseError
            If no operation has been set, or required data is missing.
        """
        if not self._operation:
            raise DatabaseError("No SQL operation has been set")

        sql, params = "", []

        if self._operation == "SELECT":
            kw  = "DISTINCT " if self._distinct else ""
            sql = f"SELECT {kw}{self._select} FROM {self.table}"
            if self._join:
                sql += " " + " ".join(self._join)
            if self._where:
                sql += " WHERE " + " ".join(self._where)
                params.extend(self._where_params)
            if self._group_by:
                sql += f" GROUP BY {self._group_by}"
            if self._having:
                sql += f" HAVING {self._having}"
            if self._order_by:
                sql += f" ORDER BY {self._order_by}"
            if self._limit is not None:
                sql += " LIMIT ?"
                params.append(self._limit)
            if self._offset is not None:
                sql += " OFFSET ?"
                params.append(self._offset)

        elif self._operation == "UPDATE":
            if not self._set_values:
                raise DatabaseError("No values provided for UPDATE")
            set_clause = ", ".join(f"{k} = ?" for k in self._set_values)
            sql = f"UPDATE {self.table} SET {set_clause}"
            params.extend(self._set_values.values())
            if self._where:
                sql += " WHERE " + " ".join(self._where)
                params.extend(self._where_params)

        elif self._operation == "INSERT":
            if not self._insert_values:
                raise DatabaseError("No values provided for INSERT")
            cols = list(self._insert_values[0].keys())
            ph   = ", ".join("?" for _ in cols)
            rows_ph = ", ".join(f"({ph})" for _ in self._insert_values)
            sql = f"INSERT INTO {self.table} ({', '.join(cols)}) VALUES {rows_ph}"
            params = [v for row in self._insert_values for v in (row[c] for c in cols)]

        elif self._operation == "DELETE":
            sql = f"DELETE FROM {self.table}"
            if self._where:
                sql += " WHERE " + " ".join(self._where)
                params.extend(self._where_params)

        return sql, params
