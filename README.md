# HandySQL - Complete Functions Reference

> 60+ core functions + 20+ SQL Builder methods = **80+ functions total**

---

## 🏗️ Table Creation

| # | Function | Description |
|---|----------|-------------|
| 1 | `create_table()` | Full table creation with schema definition |
| 2 | `quick_table()` | Quick table creation (column names only) |
| 3 | `smart_table()` | Smart table with automatic type detection |
| 4 | `drop_table()` | Delete a table |
| 5 | `table_exists()` | Check if a table exists |
| 6 | `get_tables()` | List of all tables |
| 7 | `copy_table()` | Copy a table |
| 8 | `truncate()` | Clear all rows from a table |
| 9 | `get_columns()` | List of columns |
| 10 | `column_exists()` | Check if a column exists |

---

## ➕ Inserting

| # | Function | Description |
|---|----------|-------------|
| 11 | `insert_row()` | Insert a single row |
| 12 | `insert_many()` | Insert multiple rows |
| 13 | `add()` | Shortcut: insert one record |
| 14 | `add_many()` | Shortcut: insert many records |

---

## 🔍 Finding and Fetching

| # | Function | Description |
|---|----------|-------------|
| 15 | `fetch_all()` | Fetch all records |
| 16 | `fetch_one()` | Fetch a single record |
| 17 | `find()` | Shortcut: find by condition |
| 18 | `find_by_id()` | Find by ID |
| 19 | `find_all()` | Shortcut: all matching records |
| 20 | `get_all()` | All records (with sorting) |
| 21 | `get_by_ids()` | Fetch by multiple IDs |
| 22 | `first()` | First record |
| 23 | `last()` | Last record |
| 24 | `latest()` | Newest record(s) |
| 25 | `oldest()` | Oldest record(s) |
| 26 | `random()` | Random record(s) |

---

## ✏️ Updating

| # | Function | Description |
|---|----------|-------------|
| 27 | `update_row()` | Update a record |
| 28 | `change()` | Shortcut: update by ID |
| 29 | `change_where()` | Shortcut: conditional update |
| 30 | `increment()` | Increase a number column |
| 31 | `decrement()` | Decrease a number column |
| 32 | `toggle()` | Toggle a boolean (0 ↔ 1) |
| 33 | `update_or_create()` | Update or create |
| 34 | `find_or_create()` | Find or create |

---

## ❌ Deleting

| # | Function | Description |
|---|----------|-------------|
| 35 | `delete_row()` | Delete a record |
| 36 | `delete_all()` | Delete all records ⚠️ dangerous |
| 37 | `remove()` | Shortcut: delete by ID |
| 38 | `remove_where()` | Shortcut: conditional delete |

---

## 🔎 Searching

| # | Function | Description |
|---|----------|-------------|
| 39 | `search()` | Text search (LIKE) |
| 40 | `exists()` | Check existence |
| 41 | `pluck()` | Get values from a single column |
| 42 | `distinct_values()` | Get unique values |

---

## 📊 Statistics

| # | Function | Description |
|---|----------|-------------|
| 43 | `count()` | Count records |
| 44 | `sum()` | Sum of a column |
| 45 | `avg()` | Average of a column |
| 46 | `min()` | Minimum value |
| 47 | `max()` | Maximum value |

---

## 📄 Pagination

| # | Function | Description |
|---|----------|-------------|
| 48 | `paginate()` | Pagination |
| 49 | `chunk()` | Process in chunks (generator) |

---

## 🔧 Utilities

| # | Function | Description |
|---|----------|-------------|
| 50 | `execute()` | Execute a SQL query |
| 51 | `execute_many()` | Execute multiple queries |
| 52 | `query()` | Get SQL Builder instance |
| 53 | `clone_row()` | Clone a record |
| 54 | `backup_table()` | Create a table backup |

---

## 📁 Import / Export

| # | Function | Description |
|---|----------|-------------|
| 55 | `export_to_json()` | Export to JSON |
| 56 | `import_from_json()` | Import from JSON |

---

## 🔄 Transactions

| # | Function | Description |
|---|----------|-------------|
| 57 | `begin_transaction()` | Begin a transaction |
| 58 | `commit()` | Commit (save) |
| 59 | `rollback()` | Rollback (cancel) |

---

## 🔌 Connection

| # | Function | Description |
|---|----------|-------------|
| 60 | `connect()` | Connect to database |
| 61 | `disconnect()` | Disconnect |
| 62 | `get_cursor()` | Get cursor (context manager) |

---

## 🎯 SQL Builder Methods

### SELECT Operations

| # | Method | Description |
|---|--------|-------------|
| 1 | `select()` | Select columns |
| 2 | `distinct()` | Unique values |
| 3 | `where()` | WHERE condition |
| 4 | `and_where()` | AND condition |
| 5 | `or_where()` | OR condition |
| 6 | `where_in()` | WHERE IN |
| 7 | `where_between()` | WHERE BETWEEN |
| 8 | `where_like()` | WHERE LIKE |
| 9 | `where_null()` | WHERE NULL |
| 10 | `order_by()` | Sorting |
| 11 | `group_by()` | Grouping |
| 12 | `having()` | HAVING condition |
| 13 | `limit()` | Limit results |
| 14 | `offset()` | Offset results |

### JOIN Operations

| # | Method | Description |
|---|--------|-------------|
| 15 | `join()` | INNER JOIN |
| 16 | `left_join()` | LEFT JOIN |
| 17 | `right_join()` | RIGHT JOIN |

### Other Operations

| # | Method | Description |
|---|--------|-------------|
| 18 | `insert()` | INSERT |
| 19 | `values()` | INSERT VALUES |
| 20 | `update()` | UPDATE |
| 21 | `set()` | SET values |
| 22 | `delete()` | DELETE |
| 23 | `build()` | Build SQL query |

---

## 💡 Quick Examples

### Creating a Table

```python
# Simple — column names only
db.quick_table("users", "name", "email")

# Smart — example values for type inference
db.smart_table("products", name="Phone", price=1000000)

# Full control
db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
```

### Inserting Data

```python
# Single record
db.add("users", name="Ali")

# Multiple records
db.add_many("users", {"name": "Ali"}, {"name": "Vali"})
```

### Finding Records

```python
# By ID — fastest
db.find_by_id("users", 5)

# By condition
db.find("users", email="ali@example.com")

# All records
db.get_all("users")

# Newest
db.latest("users")

# Random sample
db.random("users", limit=5)
```

### Updating

```python
# Simple update by ID
db.change("users", 5, name="New Name")

# Increment a counter
db.increment("posts", 1, "views")

# Toggle boolean flag
db.toggle("users", 5, "is_active")

# Update or create
db.update_or_create(
    "users",
    find_by={"email": "ali@example.com"},
    defaults={"name": "Ali"}
)
```

### Deleting

```python
# By ID
db.remove("users", 5)

# By condition
db.remove_where("users", status="deleted")

# Clear entire table
db.truncate("temp_data")
```

### Statistics

```python
db.count("users")
db.sum("orders", "amount")
db.avg("products", "price")
db.min("products", "price")
db.max("products", "price")
```

### Searching

```python
# Full-text search
db.search("products", "name", "phone")

# Check existence
if db.exists("users", email="ali@example.com"):
    ...

# Unique values
cities = db.distinct_values("users", "city")
```

---

## 🚀 Top 10 Most Commonly Used

1. `db.quick_table()` — Create a table
2. `db.add()` — Insert data
3. `db.find_by_id()` — Find by ID
4. `db.get_all()` — All records
5. `db.change()` — Update
6. `db.remove()` — Delete
7. `db.count()` — Count
8. `db.exists()` — Check existence
9. `db.search()` — Search
10. `db.paginate()` — Pagination
