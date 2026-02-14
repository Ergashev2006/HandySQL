# HandySQL – Project File Map

```
HandySQL/                          ← project root
│
├── HandySQL/                      ← Python package (importable)
│   ├── __init__.py               ← public API & version
│   ├── sql_easy.py               ← HandySQL main class (all 80+ methods)
│   ├── builder.py                ← SQLBuilder (fluent query builder)
│   ├── connection.py             ← Connection (low-level DB wrapper)
│   └── exceptions.py             ← DatabaseError + sub-exceptions
│
├── tests.py                      ← 56 unit tests (pytest / unittest)
├── examples.py                   ← 15 runnable usage examples
│
├── setup.py                      ← pip install config (legacy)
├── pyproject.toml                ← pip install config (modern PEP 517)
├── requirements.txt              ← optional dependencies
├── README.md                     ← full documentation
├── CHANGELOG.md                  ← version history
└── .gitignore                    ← ignored files for Git
```

---

## File descriptions

### `HandySQL/__init__.py`
Entry point for the package.
Imports and re-exports everything users need:

```python
from HandySQL import HandySQL, SQLBuilder, DatabaseError
from HandySQL import create_connection, sql_builder
```

Also exposes:
- `__version__`  → `"1.0.0"`
- `MYSQL_AVAILABLE`  → `True / False`
- `POSTGRESQL_AVAILABLE`  → `True / False`

---

### `HandySQL/sql_easy.py`
The **main class** – `HandySQL`.  
Contains 80+ methods organised in sections:

| Section | Methods |
|---------|---------|
| Table management | `create_table`, `quick_table`, `smart_table`, `drop_table`, `table_exists`, `get_tables`, `get_columns`, `column_exists`, `copy_table`, `truncate` |
| Insert | `insert_row`, `insert_many`, `add`, `add_many` |
| Select / Fetch | `fetch_all`, `fetch_one`, `find`, `find_by_id`, `find_all`, `get_all`, `get_by_ids`, `first`, `last`, `latest`, `oldest`, `random` |
| Search | `search`, `exists`, `pluck`, `distinct_values`, `chunk` |
| Update | `update_row`, `change`, `change_where`, `increment`, `decrement`, `toggle`, `update_or_create`, `find_or_create`, `clone_row` |
| Delete | `delete_row`, `delete_all`, `remove`, `remove_where` |
| Aggregates | `count`, `sum`, `avg`, `min`, `max` |
| Pagination | `paginate` |
| Backup / IO | `backup_table`, `export_to_json`, `import_from_json` |
| Transactions | `begin_transaction`, `commit`, `rollback` |
| Connection | `connect`, `disconnect`, `get_cursor` |

---

### `HandySQL/builder.py`
**`SQLBuilder`** – chainable query builder.

```python
from HandySQL import sql_builder

q = (sql_builder("users")
        .select(["name", "email"])
        .where("age > ?", 18)
        .where_in("status", ["active", "verified"])
        .order_by("name")
        .limit(20))

sql, params = q.build()
```

Supported methods:

| Category | Methods |
|----------|---------|
| SELECT | `select`, `distinct` |
| WHERE | `where`, `and_where`, `or_where`, `where_in`, `where_between`, `where_like`, `where_null` |
| ORDER / GROUP | `order_by`, `group_by`, `having` |
| PAGING | `limit`, `offset` |
| JOIN | `join`, `left_join`, `right_join` |
| INSERT | `insert`, `values` |
| UPDATE | `update`, `set` |
| DELETE | `delete` |
| Build | `build` → `(sql, params)` |

---

### `HandySQL/connection.py`
**`Connection`** – thin wrapper around the raw DB-API connection.  
Used internally by `HandySQL`; can also be used standalone.

Responsibilities:
- Open / close connection
- Provide `cursor()` context manager (auto commit / rollback)
- `execute(sql, params)` → rows or rowcount
- `execute_many(sql, params_list)` → rowcount
- `begin()` / `commit()` / `rollback()`

---

### `HandySQL/exceptions.py`
Exception hierarchy:

```
Exception
└── DatabaseError          ← base for all HandySQL errors
    ├── ConnectionError    ← cannot reach the database
    ├── TableNotFoundError ← table does not exist
    ├── RecordNotFoundError← row not found (e.g. clone_row)
    └── ValidationError   ← safety check failed (empty filter, etc.)
```

---

### `tests.py`
**56 unit tests** covering:
- `SQLBuilder` (13 tests)
- `HandySQL` – table helpers, insert, select, update, delete,
  aggregates, pagination, copy, truncate (40 tests)
- Context manager (3 tests)

Run with:
```bash
python tests.py
# or
pytest tests.py -v
```

---

### `examples.py`
**15 commented examples**:

| # | Topic |
|---|-------|
| 1 | Quick table creation |
| 2 | Smart table (auto types) |
| 3 | Insert & find |
| 4 | Update |
| 5 | Delete |
| 6 | Bulk insert |
| 7 | Existence check |
| 8 | Search |
| 9 | Statistics |
| 10 | Pagination |
| 11 | increment / decrement / toggle |
| 12 | update_or_create / find_or_create |
| 13 | SQL Builder (advanced queries) |
| 14 | Transactions |
| 15 | Context manager |

---

## Installation

```bash
# SQLite (no extra packages needed)
pip install -e .

# MySQL support
pip install -e ".[mysql]"

# PostgreSQL support
pip install -e ".[postgresql]"

# All databases
pip install -e ".[all]"

# Development tools
pip install -e ".[dev]"
```

## Quick import reference

```python
from HandySQL import HandySQL            # main class
from HandySQL import sql_builder        # standalone builder
from HandySQL import create_connection  # factory function
from HandySQL import DatabaseError      # base exception
from HandySQL import SQLBuilder         # builder class
```
