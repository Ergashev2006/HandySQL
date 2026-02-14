# sql_easy.py - Simple and powerful SQL library
"""
HandySQL - A simple and powerful SQL library for Python

Supported databases:
- SQLite
- MySQL
- PostgreSQL

Example:
    from sql_easy import HandySQL

    db = HandySQL(db_type="sqlite", database="mydb.db")
    db.connect()

    # Create table
    db.create_table("users", {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "email": "TEXT UNIQUE"
    })

    # Insert record
    db.insert_row("users", name="John", email="john@example.com")

    # Fetch records
    users = db.fetch_all("users")
"""

import sqlite3
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

from typing import Optional, List, Dict, Any, Union, Tuple
from contextlib import contextmanager
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass


class SQLBuilder:
    """Builder pattern for constructing SQL queries"""

    def __init__(self, table: str = None):
        self.table = table
        self._select = "*"
        self._where = []
        self._where_params = []
        self._order_by = None
        self._limit = None
        self._offset = None
        self._join = []
        self._set_values = {}
        self._insert_values = []
        self._operation = None
        self._group_by = None
        self._having = None
        self._distinct = False

    def select(self, columns: Union[str, List[str]] = "*") -> 'SQLBuilder':
        """Start a SELECT query"""
        self._operation = 'SELECT'
        if isinstance(columns, list):
            self._select = ", ".join(columns)
        else:
            self._select = columns
        return self

    def distinct(self) -> 'SQLBuilder':
        """Add DISTINCT keyword"""
        self._distinct = True
        return self

    def where(self, condition: str, *params) -> 'SQLBuilder':
        """Add a WHERE condition (automatically adds AND if conditions already exist)"""
        if self._where:
            self._where.append(f"AND {condition}")
        else:
            self._where.append(condition)
        self._where_params.extend(params)
        return self

    def and_where(self, condition: str, *params) -> 'SQLBuilder':
        """Add an AND WHERE condition"""
        if self._where:
            self._where.append(f"AND {condition}")
        else:
            self._where.append(condition)
        self._where_params.extend(params)
        return self

    def or_where(self, condition: str, *params) -> 'SQLBuilder':
        """Add an OR WHERE condition"""
        if self._where:
            self._where.append(f"OR {condition}")
        else:
            self._where.append(condition)
        self._where_params.extend(params)
        return self

    def where_in(self, column: str, values: List[Any]) -> 'SQLBuilder':
        """Add a WHERE IN condition"""
        placeholders = ", ".join(["?" for _ in values])
        self._where.append(f"{column} IN ({placeholders})")
        self._where_params.extend(values)
        return self

    def where_between(self, column: str, start: Any, end: Any) -> 'SQLBuilder':
        """Add a WHERE BETWEEN condition"""
        self._where.append(f"{column} BETWEEN ? AND ?")
        self._where_params.extend([start, end])
        return self

    def where_like(self, column: str, pattern: str) -> 'SQLBuilder':
        """Add a WHERE LIKE condition"""
        self._where.append(f"{column} LIKE ?")
        self._where_params.append(pattern)
        return self

    def where_null(self, column: str, is_null: bool = True) -> 'SQLBuilder':
        """Add WHERE IS NULL or IS NOT NULL"""
        if is_null:
            self._where.append(f"{column} IS NULL")
        else:
            self._where.append(f"{column} IS NOT NULL")
        return self

    def order_by(self, column: str, direction: str = "ASC") -> 'SQLBuilder':
        """Add ORDER BY clause"""
        self._order_by = f"{column} {direction}"
        return self

    def group_by(self, columns: Union[str, List[str]]) -> 'SQLBuilder':
        """Add GROUP BY clause"""
        if isinstance(columns, list):
            self._group_by = ", ".join(columns)
        else:
            self._group_by = columns
        return self

    def having(self, condition: str) -> 'SQLBuilder':
        """Add HAVING condition"""
        self._having = condition
        return self

    def limit(self, limit: int) -> 'SQLBuilder':
        """Add LIMIT clause"""
        self._limit = limit
        return self

    def offset(self, offset: int) -> 'SQLBuilder':
        """Add OFFSET clause"""
        self._offset = offset
        return self

    def join(self, table: str, on: str, join_type: str = "INNER") -> 'SQLBuilder':
        """Add a JOIN clause"""
        self._join.append(f"{join_type} JOIN {table} ON {on}")
        return self

    def left_join(self, table: str, on: str) -> 'SQLBuilder':
        """Add a LEFT JOIN clause"""
        return self.join(table, on, "LEFT")

    def right_join(self, table: str, on: str) -> 'SQLBuilder':
        """Add a RIGHT JOIN clause"""
        return self.join(table, on, "RIGHT")

    def update(self, table: str) -> 'SQLBuilder':
        """Start an UPDATE query"""
        self._operation = 'UPDATE'
        self.table = table
        return self

    def set(self, **kwargs) -> 'SQLBuilder':
        """Set values for UPDATE"""
        self._set_values.update(kwargs)
        return self

    def insert(self, table: str) -> 'SQLBuilder':
        """Start an INSERT query"""
        self._operation = 'INSERT'
        self.table = table
        return self

    def values(self, **kwargs) -> 'SQLBuilder':
        """Set values for INSERT"""
        self._insert_values.append(kwargs)
        return self

    def delete(self, table: str) -> 'SQLBuilder':
        """Start a DELETE query"""
        self._operation = 'DELETE'
        self.table = table
        return self

    def build(self) -> Tuple[str, List]:
        """Build and return the SQL query string and its parameters"""
        if not self._operation:
            raise DatabaseError("No SQL operation has been set")

        sql = ""
        params = []

        if self._operation == 'SELECT':
            distinct_keyword = "DISTINCT " if self._distinct else ""
            sql = f"SELECT {distinct_keyword}{self._select} FROM {self.table}"

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

        elif self._operation == 'UPDATE':
            if not self._set_values:
                raise DatabaseError("No values provided for UPDATE")
            set_clause = ", ".join([f"{k} = ?" for k in self._set_values.keys()])
            sql = f"UPDATE {self.table} SET {set_clause}"
            params.extend(self._set_values.values())
            if self._where:
                sql += " WHERE " + " ".join(self._where)
                params.extend(self._where_params)

        elif self._operation == 'INSERT':
            if not self._insert_values:
                raise DatabaseError("No values provided for INSERT")
            columns = list(self._insert_values[0].keys())
            placeholders = ", ".join(["?" for _ in columns])
            columns_str = ", ".join(columns)
            all_values = []
            for row in self._insert_values:
                all_values.extend([row[col] for col in columns])
            values_placeholders = ", ".join(
                ["(" + placeholders + ")" for _ in self._insert_values]
            )
            sql = f"INSERT INTO {self.table} ({columns_str}) VALUES {values_placeholders}"
            params = all_values

        elif self._operation == 'DELETE':
            sql = f"DELETE FROM {self.table}"
            if self._where:
                sql += " WHERE " + " ".join(self._where)
                params.extend(self._where_params)

        return sql, params


class HandySQL:
    """Main HandySQL class"""

    def __init__(self, db_type: str = "sqlite", **kwargs):
        """
        Initialise a database connection.

        Args:
            db_type: "sqlite", "mysql", or "postgresql"
            **kwargs: Connection parameters

        SQLite:
            database (str): File path, default ":memory:"

        MySQL:
            host (str): default "localhost"
            user (str): default "root"
            password (str)
            database (str)
            port (int): default 3306

        PostgreSQL:
            host (str): default "localhost"
            user (str): default "postgres"
            password (str)
            database (str)
            port (int): default 5432
        """
        self.db_type = db_type.lower()
        self.connection_params = kwargs
        self.connection = None
        self._auto_commit = kwargs.get("auto_commit", True)

        if self.db_type == "sqlite":
            self.db_path = kwargs.get("database", ":memory:")
        elif self.db_type == "mysql":
            if not MYSQL_AVAILABLE:
                raise DatabaseError(
                    "mysql-connector-python is not installed. "
                    "Run: pip install mysql-connector-python"
                )
            self.host     = kwargs.get("host", "localhost")
            self.user     = kwargs.get("user", "root")
            self.password = kwargs.get("password", "")
            self.database = kwargs.get("database", "")
            self.port     = kwargs.get("port", 3306)
        elif self.db_type == "postgresql":
            if not POSTGRESQL_AVAILABLE:
                raise DatabaseError(
                    "psycopg2 is not installed. "
                    "Run: pip install psycopg2-binary"
                )
            self.host     = kwargs.get("host", "localhost")
            self.user     = kwargs.get("user", "postgres")
            self.password = kwargs.get("password", "")
            self.database = kwargs.get("database", "")
            self.port     = kwargs.get("port", 5432)
        else:
            raise DatabaseError(
                f"Unsupported database type: '{db_type}'. "
                "Choose 'sqlite', 'mysql', or 'postgresql'."
            )

    # ------------------------------------------------------------------ #
    #  Connection management
    # ------------------------------------------------------------------ #

    def connect(self):
        """Open the database connection"""
        if self.connection is not None:
            return self.connection
        try:
            if self.db_type == "sqlite":
                self.connection = sqlite3.connect(self.db_path)
                self.connection.row_factory = sqlite3.Row
                logger.info(f"Connected to SQLite: {self.db_path}")
            elif self.db_type == "mysql":
                self.connection = mysql.connector.connect(
                    host=self.host, user=self.user,
                    password=self.password, database=self.database,
                    port=self.port
                )
                logger.info(f"Connected to MySQL: {self.database}")
            elif self.db_type == "postgresql":
                self.connection = psycopg2.connect(
                    host=self.host, user=self.user,
                    password=self.password, database=self.database,
                    port=self.port
                )
                logger.info(f"Connected to PostgreSQL: {self.database}")
            return self.connection
        except Exception as e:
            raise DatabaseError(f"Connection failed: {e}")

    def disconnect(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    @contextmanager
    def get_cursor(self):
        """Context manager that provides a cursor and handles commit/rollback"""
        if self.connection is None:
            self.connect()
        cursor = self.connection.cursor()
        try:
            yield cursor
            if self._auto_commit:
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Operation failed, rolled back: {e}")
            raise DatabaseError(f"Database operation error: {e}")
        finally:
            cursor.close()

    # ------------------------------------------------------------------ #
    #  Query execution
    # ------------------------------------------------------------------ #

    def execute(self, sql: str, params: Union[Tuple, List] = None) -> Any:
        """
        Execute a raw SQL statement.

        Returns:
            SELECT  -> List[Dict]
            Other   -> number of affected rows (int)
        """
        with self.get_cursor() as cursor:
            logger.debug(f"SQL: {sql} | params: {params}")
            cursor.execute(sql, params or ())

            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                if self.db_type == "sqlite":
                    return [dict(r) for r in rows]
                else:
                    cols = [c[0] for c in cursor.description]
                    return [dict(zip(cols, r)) for r in rows]
            return cursor.rowcount

    def execute_many(self, sql: str, params_list: List[Tuple]) -> int:
        """Execute a parameterised statement for each item in params_list"""
        with self.get_cursor() as cursor:
            cursor.executemany(sql, params_list)
            return cursor.rowcount

    def query(self, table: str = None) -> SQLBuilder:
        """Return a fresh SQLBuilder for the given table"""
        return SQLBuilder(table)

    # ------------------------------------------------------------------ #
    #  Table management
    # ------------------------------------------------------------------ #

    def create_table(
        self,
        table: str,
        columns: Dict[str, str],
        primary_key: str = None,
        foreign_keys: List[Dict] = None,
        if_not_exists: bool = True,
    ):
        """
        Create a table.

        Args:
            table         : Table name
            columns       : {column_name: sql_type, ...}
            primary_key   : Composite primary key column (optional)
            foreign_keys  : [{"column": ..., "references": ...}, ...]
            if_not_exists : Skip silently if table already exists

        Example:
            db.create_table("users", {
                "id":    "INTEGER PRIMARY KEY AUTOINCREMENT",
                "name":  "TEXT NOT NULL",
                "email": "TEXT UNIQUE",
            })
        """
        col_defs = [f"{n} {t}" for n, t in columns.items()]
        if primary_key:
            col_defs.append(f"PRIMARY KEY ({primary_key})")
        if foreign_keys:
            for fk in foreign_keys:
                col_defs.append(
                    f"FOREIGN KEY ({fk['column']}) REFERENCES {fk['references']}"
                )
        prefix = "IF NOT EXISTS " if if_not_exists else ""
        sql = f"CREATE TABLE {prefix}{table} ({', '.join(col_defs)})"
        logger.info(f"Creating table: {table}")
        return self.execute(sql)

    def quick_table(self, table: str, *columns, auto_id: bool = True):
        """
        Create a table with TEXT columns and an optional auto-increment ID.

        Example:
            db.quick_table("users", "name", "email", "phone")
            # columns: id (auto), name, email, phone
        """
        cols = {}
        if auto_id:
            id_types = {
                "sqlite":     "INTEGER PRIMARY KEY AUTOINCREMENT",
                "mysql":      "INT AUTO_INCREMENT PRIMARY KEY",
                "postgresql": "SERIAL PRIMARY KEY",
            }
            cols["id"] = id_types[self.db_type]
        for col in columns:
            cols[col] = "TEXT"
        return self.create_table(table, cols)

    def smart_table(self, table: str, **columns):
        """
        Create a table whose column types are inferred from example values.

        Example:
            db.smart_table("products",
                name="Phone",      # -> TEXT
                price=1500000,     # -> INTEGER
                rating=4.5,        # -> REAL
                in_stock=True,     # -> INTEGER (0/1)
            )
        """
        id_types = {
            "sqlite":     "INTEGER PRIMARY KEY AUTOINCREMENT",
            "mysql":      "INT AUTO_INCREMENT PRIMARY KEY",
            "postgresql": "SERIAL PRIMARY KEY",
        }
        cols = {"id": id_types[self.db_type]}
        for name, example in columns.items():
            if isinstance(example, bool):
                cols[name] = "INTEGER"
            elif isinstance(example, int):
                cols[name] = "INTEGER"
            elif isinstance(example, float):
                cols[name] = "REAL"
            else:
                cols[name] = "TEXT"
        return self.create_table(table, cols)

    def drop_table(self, table: str, if_exists: bool = True):
        """Drop a table"""
        prefix = "IF EXISTS " if if_exists else ""
        logger.warning(f"Dropping table: {table}")
        return self.execute(f"DROP TABLE {prefix}{table}")

    def table_exists(self, table: str) -> bool:
        """Return True if the table exists"""
        if self.db_type == "sqlite":
            res = self.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,),
            )
        elif self.db_type == "mysql":
            res = self.execute("SHOW TABLES LIKE %s", (table,))
        else:
            res = self.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_name=%s",
                (table,),
            )
        return len(res) > 0

    def get_tables(self) -> List[str]:
        """Return a list of all table names"""
        if self.db_type == "sqlite":
            rows = self.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [r['name'] for r in rows]
        elif self.db_type == "mysql":
            rows = self.execute("SHOW TABLES")
            return [list(r.values())[0] for r in rows]
        else:
            rows = self.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public'"
            )
            return [r['table_name'] for r in rows]

    def get_columns(self, table: str) -> List[str]:
        """Return a list of column names for a table"""
        if self.db_type == "sqlite":
            # Use SELECT so execute() returns rows instead of rowcount
            rows = self.execute(
                "SELECT name FROM pragma_table_info(?)", (table,)
            )
            return [r['name'] for r in rows]
        elif self.db_type == "mysql":
            rows = self.execute(f"SHOW COLUMNS FROM {table}")
            return [r['Field'] for r in rows]
        else:
            rows = self.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name=%s ORDER BY ordinal_position",
                (table,),
            )
            return [r['column_name'] for r in rows]

    def column_exists(self, table: str, column: str) -> bool:
        """Return True if the column exists in the table"""
        return column in self.get_columns(table)

    def copy_table(self, source: str, destination: str, if_exists: str = "fail") -> int:
        """
        Copy a table (structure + data).

        if_exists: 'fail' | 'replace' | 'append'
        Returns number of rows in destination after copy.
        """
        if self.table_exists(destination):
            if if_exists == "fail":
                raise DatabaseError(f"Table '{destination}' already exists")
            elif if_exists == "replace":
                self.drop_table(destination)

        if if_exists != "append":
            self.execute(f"CREATE TABLE {destination} AS SELECT * FROM {source}")
        else:
            data = self.fetch_all(source)
            if data:
                self.insert_many(destination, data)
        return self.count(destination)

    def truncate(self, table: str) -> int:
        """Remove all rows from a table (irreversible!)"""
        sql = f"DELETE FROM {table}" if self.db_type == "sqlite" else f"TRUNCATE TABLE {table}"
        logger.warning(f"Truncating table: {table}")
        return self.execute(sql)

    # ------------------------------------------------------------------ #
    #  INSERT
    # ------------------------------------------------------------------ #

    def insert_row(self, table: str, **data) -> int:
        """Insert a single row"""
        builder = self.query().insert(table).values(**data)
        sql, params = builder.build()
        return self.execute(sql, params)

    def insert_many(self, table: str, rows: List[Dict]) -> int:
        """Insert multiple rows efficiently"""
        if not rows:
            return 0
        cols = list(rows[0].keys())
        placeholders = ", ".join(["?" for _ in cols])
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
        return self.execute_many(sql, [tuple(r[c] for c in cols) for r in rows])

    def add(self, table: str, **data) -> int:
        """Shorthand: insert one row.  db.add("users", name="John")"""
        return self.insert_row(table, **data)

    def add_many(self, table: str, *rows) -> int:
        """Shorthand: insert many rows.  db.add_many("users", {...}, {...})"""
        return self.insert_many(table, list(rows))

    # ------------------------------------------------------------------ #
    #  SELECT / FETCH
    # ------------------------------------------------------------------ #

    def fetch_all(
        self, table: str, columns: Union[str, List[str]] = None, **filters
    ) -> List[Dict]:
        """Fetch all rows, optionally filtered"""
        builder = self.query(table).select(columns or "*")
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        sql, params = builder.build()
        return self.execute(sql, params)

    def fetch_one(
        self, table: str, columns: Union[str, List[str]] = None, **filters
    ) -> Optional[Dict]:
        """Fetch the first matching row"""
        builder = self.query(table).select(columns or "*")
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        builder.limit(1)
        sql, params = builder.build()
        result = self.execute(sql, params)
        return result[0] if result else None

    def find(self, table: str, **filters) -> Optional[Dict]:
        """Shorthand for fetch_one.  db.find("users", email="x@y.com")"""
        return self.fetch_one(table, **filters)

    def find_by_id(self, table: str, id_value: Any) -> Optional[Dict]:
        """Find a row by primary key.  db.find_by_id("users", 5)"""
        return self.fetch_one(table, id=id_value)

    def find_all(self, table: str, **filters) -> List[Dict]:
        """Shorthand for fetch_all.  db.find_all("users", status="active")"""
        return self.fetch_all(table, **filters)

    def get_all(self, table: str, order_by: str = None) -> List[Dict]:
        """
        Fetch every row, with optional sorting.

        Example:
            db.get_all("users", order_by="name ASC")
        """
        if order_by:
            parts = order_by.split()
            col, direction = parts[0], (parts[1] if len(parts) > 1 else "ASC")
            builder = self.query(table).select("*").order_by(col, direction)
            sql, params = builder.build()
            return self.execute(sql, params)
        return self.fetch_all(table)

    def get_by_ids(self, table: str, ids: List[Any]) -> List[Dict]:
        """Fetch rows whose ID is in the supplied list"""
        builder = self.query(table).select("*").where_in("id", ids)
        sql, params = builder.build()
        return self.execute(sql, params)

    def first(self, table: str, order_by: str = "id ASC") -> Optional[Dict]:
        """Fetch the first row according to order_by"""
        parts = order_by.split()
        col, direction = parts[0], (parts[1] if len(parts) > 1 else "ASC")
        builder = self.query(table).select("*").order_by(col, direction).limit(1)
        sql, params = builder.build()
        result = self.execute(sql, params)
        return result[0] if result else None

    def last(self, table: str, order_by: str = "id DESC") -> Optional[Dict]:
        """Fetch the last row according to order_by"""
        return self.first(table, order_by)

    def latest(self, table: str, column: str = "id", limit: int = 1) -> Union[Dict, List[Dict]]:
        """
        Fetch the most-recent row(s) by column (DESC).

        Returns a single dict when limit=1, a list otherwise.
        """
        builder = self.query(table).select("*").order_by(column, "DESC").limit(limit)
        sql, params = builder.build()
        results = self.execute(sql, params)
        return (results[0] if results else None) if limit == 1 else results

    def oldest(self, table: str, column: str = "id", limit: int = 1) -> Union[Dict, List[Dict]]:
        """
        Fetch the oldest row(s) by column (ASC).

        Returns a single dict when limit=1, a list otherwise.
        """
        builder = self.query(table).select("*").order_by(column, "ASC").limit(limit)
        sql, params = builder.build()
        results = self.execute(sql, params)
        return (results[0] if results else None) if limit == 1 else results

    def random(self, table: str, limit: int = 1, **filters) -> Union[Dict, List[Dict]]:
        """
        Fetch random row(s).

        Returns a single dict when limit=1, a list otherwise.
        """
        builder = self.query(table).select("*")
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        rand_fn = "RAND()" if self.db_type == "mysql" else "RANDOM()"
        builder.order_by(rand_fn, "")
        builder.limit(limit)
        sql, params = builder.build()
        results = self.execute(sql, params)
        return (results[0] if results else None) if limit == 1 else results

    def pluck(self, table: str, column: str, **filters) -> List[Any]:
        """
        Return a flat list of values from one column.

        Example:
            emails = db.pluck("users", "email")
        """
        builder = self.query(table).select(column)
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        sql, params = builder.build()
        return [row[column] for row in self.execute(sql, params)]

    def distinct_values(self, table: str, column: str) -> List[Any]:
        """Return unique, non-null values of a column"""
        builder = self.query(table).select(column).distinct()
        sql, params = builder.build()
        return [r[column] for r in self.execute(sql, params) if r[column] is not None]

    def chunk(self, table: str, size: int = 100, **filters):
        """
        Iterate over a table in fixed-size chunks (generator).

        Example:
            for batch in db.chunk("users", size=100):
                for user in batch:
                    process(user)
        """
        offset = 0
        while True:
            builder = self.query(table).select("*")
            for k, v in filters.items():
                builder.where(f"{k} = ?", v)
            builder.limit(size).offset(offset)
            sql, params = builder.build()
            results = self.execute(sql, params)
            if not results:
                break
            yield results
            offset += size

    def search(self, table: str, column: str, keyword: str) -> List[Dict]:
        """
        Find rows where column LIKE '%keyword%'.

        Example:
            results = db.search("products", "name", "phone")
        """
        builder = self.query(table).select("*").where_like(column, f"%{keyword}%")
        sql, params = builder.build()
        return self.execute(sql, params)

    def exists(self, table: str, **conditions) -> bool:
        """Return True if at least one matching row exists"""
        return self.fetch_one(table, **conditions) is not None

    # ------------------------------------------------------------------ #
    #  UPDATE
    # ------------------------------------------------------------------ #

    def update_row(self, table: str, data: Dict, **filters) -> int:
        """Update rows matching filters with the values in data"""
        builder = self.query().update(table).set(**data)
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        sql, params = builder.build()
        return self.execute(sql, params)

    def change(self, table: str, id_value: Any, **changes) -> int:
        """
        Update a single row by ID.

        Example:
            db.change("users", 5, name="New Name", age=30)
        """
        return self.update_row(table, changes, id=id_value)

    def change_where(self, table: str, changes: Dict, **conditions) -> int:
        """
        Update rows matching conditions.

        Example:
            db.change_where("users", {"status": "inactive"}, age=18)
        """
        return self.update_row(table, changes, **conditions)

    def increment(self, table: str, id_value: Any, column: str, amount: int = 1) -> int:
        """
        Add `amount` to a numeric column (default +1).

        Example:
            db.increment("posts", post_id, "views")
            db.increment("wallets", user_id, "balance", 500)
        """
        row = self.find_by_id(table, id_value)
        if not row:
            raise DatabaseError(f"Row with id={id_value} not found")
        try:
            new_value = int(row.get(column) or 0) + amount
        except (ValueError, TypeError):
            raise DatabaseError(f"Column '{column}' is not numeric")
        return self.update_row(table, {column: new_value}, id=id_value)

    def decrement(self, table: str, id_value: Any, column: str, amount: int = 1) -> int:
        """
        Subtract `amount` from a numeric column (default -1).

        Example:
            db.decrement("products", product_id, "stock")
            db.decrement("wallets", user_id, "balance", 200)
        """
        return self.increment(table, id_value, column, -amount)

    def toggle(self, table: str, id_value: Any, column: str) -> int:
        """
        Flip a boolean (integer 0/1) column.

        Example:
            db.toggle("users", user_id, "is_active")
        """
        row = self.find_by_id(table, id_value)
        if not row:
            raise DatabaseError(f"Row with id={id_value} not found")
        new_value = 0 if int(row.get(column, 0)) else 1
        return self.update_row(table, {column: new_value}, id=id_value)

    def update_or_create(self, table: str, find_by: Dict, defaults: Dict = None) -> tuple:
        """
        Update an existing row or create a new one.

        Returns (row_dict, was_created).

        Example:
            setting, created = db.update_or_create(
                "settings",
                find_by={"user_id": "1"},
                defaults={"theme": "dark"},
            )
        """
        defaults = defaults or {}
        existing = self.fetch_one(table, **find_by)
        if existing:
            if defaults:
                self.update_row(table, defaults, **find_by)
                return self.fetch_one(table, **find_by), False
            return existing, False
        self.insert_row(table, **{**find_by, **defaults})
        return self.fetch_one(table, **find_by), True

    def find_or_create(self, table: str, **data) -> tuple:
        """
        Return an existing row or create it.

        Returns (row_dict, was_created).

        Example:
            tag, created = db.find_or_create("tags", name="Python")
        """
        existing = self.fetch_one(table, **data)
        if existing:
            return existing, False
        self.insert_row(table, **data)
        return self.fetch_one(table, **data), True

    def clone_row(self, table: str, id_value: Any, **changes) -> int:
        """
        Duplicate a row, optionally overriding fields.

        Example:
            db.clone_row("products", 5, name="Copy of Phone")
        """
        original = self.find_by_id(table, id_value)
        if not original:
            raise DatabaseError(f"Row with id={id_value} not found")
        new_row = {k: v for k, v in original.items() if k != 'id'}
        new_row.update(changes)
        return self.insert_row(table, **new_row)

    # ------------------------------------------------------------------ #
    #  DELETE
    # ------------------------------------------------------------------ #

    def delete_row(self, table: str, **filters) -> int:
        """Delete rows matching filters (at least one filter required)"""
        if not filters:
            raise DatabaseError("Safety: delete_row() requires at least one filter")
        builder = self.query().delete(table)
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        sql, params = builder.build()
        return self.execute(sql, params)

    def delete_all(self, table: str, confirm: bool = False) -> int:
        """Delete ALL rows from a table.  Pass confirm=True to proceed."""
        if not confirm:
            raise DatabaseError("Pass confirm=True to delete all rows")
        return self.execute(f"DELETE FROM {table}")

    def remove(self, table: str, id_value: Any) -> int:
        """Delete a row by ID.  db.remove("users", 5)"""
        return self.delete_row(table, id=id_value)

    def remove_where(self, table: str, **conditions) -> int:
        """Delete rows matching conditions.  db.remove_where("users", status="deleted")"""
        if not conditions:
            raise DatabaseError("Safety: remove_where() requires at least one condition")
        return self.delete_row(table, **conditions)

    # ------------------------------------------------------------------ #
    #  Aggregates
    # ------------------------------------------------------------------ #

    def count(self, table: str, **filters) -> int:
        """Count rows, optionally filtered"""
        builder = self.query(table).select("COUNT(*) as count")
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        sql, params = builder.build()
        result = self.execute(sql, params)
        return result[0]['count'] if result else 0

    def sum(self, table: str, column: str, **filters) -> float:
        """Sum a numeric column, optionally filtered"""
        builder = self.query(table).select(f"SUM({column}) as total")
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        sql, params = builder.build()
        result = self.execute(sql, params)
        return result[0]['total'] if result and result[0]['total'] is not None else 0

    def avg(self, table: str, column: str, **filters) -> float:
        """Average a numeric column, optionally filtered"""
        builder = self.query(table).select(f"AVG({column}) as average")
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        sql, params = builder.build()
        result = self.execute(sql, params)
        return result[0]['average'] if result and result[0]['average'] is not None else 0

    def min(self, table: str, column: str, **filters) -> Any:
        """Find the minimum value of a column, optionally filtered"""
        builder = self.query(table).select(f"MIN({column}) as minimum")
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        sql, params = builder.build()
        result = self.execute(sql, params)
        return result[0]['minimum'] if result else None

    def max(self, table: str, column: str, **filters) -> Any:
        """Find the maximum value of a column, optionally filtered"""
        builder = self.query(table).select(f"MAX({column}) as maximum")
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        sql, params = builder.build()
        result = self.execute(sql, params)
        return result[0]['maximum'] if result else None

    # ------------------------------------------------------------------ #
    #  Pagination
    # ------------------------------------------------------------------ #

    def paginate(self, table: str, page: int = 1, per_page: int = 10, **filters) -> Dict:
        """
        Paginate rows.

        Returns a dict: {data, page, per_page, total, pages}

        Example:
            result = db.paginate("users", page=2, per_page=10)
        """
        total = self.count(table, **filters)
        pages = (total + per_page - 1) // per_page
        builder = self.query(table).select("*")
        for k, v in filters.items():
            builder.where(f"{k} = ?", v)
        builder.limit(per_page).offset((page - 1) * per_page)
        sql, params = builder.build()
        return {
            'data': self.execute(sql, params),
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
        }

    # ------------------------------------------------------------------ #
    #  Backup / Import / Export
    # ------------------------------------------------------------------ #

    def backup_table(self, table: str, backup_table: str = None):
        """Copy table to {table}_backup (or a custom name)"""
        backup_table = backup_table or f"{table}_backup"
        logger.info(f"Backing up: {table} -> {backup_table}")
        return self.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM {table}")

    def export_to_json(self, table: str, filepath: str, **filters):
        """Export a table to a JSON file"""
        data = self.fetch_all(table, **filters)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Exported to JSON: {filepath}")

    def import_from_json(self, table: str, filepath: str):
        """Import records from a JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data:
            self.insert_many(table, data)
            logger.info(f"Imported {len(data)} rows from {filepath}")

    # ------------------------------------------------------------------ #
    #  Transactions
    # ------------------------------------------------------------------ #

    def begin_transaction(self):
        """Begin a manual transaction (disables auto-commit)"""
        if self.connection is None:
            self.connect()
        self._auto_commit = False
        logger.info("Transaction started")

    def commit(self):
        """Commit the current transaction"""
        if self.connection:
            self.connection.commit()
            logger.info("Transaction committed")

    def rollback(self):
        """Roll back the current transaction"""
        if self.connection:
            self.connection.rollback()
            logger.info("Transaction rolled back")


# ------------------------------------------------------------------ #
#  Module-level helpers
# ------------------------------------------------------------------ #

def create_connection(db_type: str = "sqlite", **kwargs) -> HandySQL:
    """
    Create and return an HandySQL instance.

    Example:
        db = create_connection("sqlite", database="app.db")
    """
    return HandySQL(db_type, **kwargs)


def sql_builder(table: str = None) -> SQLBuilder:
    """
    Return a standalone SQLBuilder.

    Example:
        q = sql_builder("users").select("*").where("age > ?", 18)
    """
    return SQLBuilder(table)


__version__ = "1.0.0"
__author__ = "HandySQL Team"


if __name__ == "__main__":
    print("HandySQL library loaded!")
    print(f"Version : {__version__}")
    print("\nSupported databases:")
    print("  SQLite     : Yes")
    print(f"  MySQL      : {'Yes' if MYSQL_AVAILABLE else 'No  (pip install mysql-connector-python)'}")
    print(f"  PostgreSQL : {'Yes' if POSTGRESQL_AVAILABLE else 'No  (pip install psycopg2-binary)'}")
