"""
HandySQL - Unit Tests (English)
"""

import unittest
from HandySQL import HandySQL, SQLBuilder, DatabaseError


class TestSQLBuilder(unittest.TestCase):
    """Tests for the SQLBuilder class"""

    def test_simple_select(self):
        sql, params = SQLBuilder("users").select("*").build()
        self.assertEqual(sql, "SELECT * FROM users")
        self.assertEqual(params, [])

    def test_select_with_columns(self):
        sql, _ = SQLBuilder("users").select(["name", "email"]).build()
        self.assertEqual(sql, "SELECT name, email FROM users")

    def test_where(self):
        sql, params = SQLBuilder("users").select("*").where("age > ?", 25).build()
        self.assertEqual(sql, "SELECT * FROM users WHERE age > ?")
        self.assertEqual(params, [25])

    def test_and_where(self):
        sql, params = (SQLBuilder("users").select("*")
                       .where("age > ?", 20).and_where("age < ?", 30).build())
        self.assertIn("AND", sql)
        self.assertEqual(params, [20, 30])

    def test_order_by(self):
        sql, _ = SQLBuilder("users").select("*").order_by("name", "ASC").build()
        self.assertIn("ORDER BY name ASC", sql)

    def test_limit(self):
        sql, params = SQLBuilder("users").select("*").limit(10).build()
        self.assertIn("LIMIT ?", sql)
        self.assertIn(10, params)

    def test_insert(self):
        sql, params = SQLBuilder().insert("users").values(name="Alice", age=25).build()
        self.assertIn("INSERT INTO users", sql)
        self.assertIn("Alice", params)
        self.assertIn(25, params)

    def test_update(self):
        sql, params = (SQLBuilder().update("users")
                       .set(name="Bob").where("id = ?", 1).build())
        self.assertIn("UPDATE users SET", sql)
        self.assertIn("Bob", params)
        self.assertIn(1, params)

    def test_delete(self):
        sql, params = SQLBuilder().delete("users").where("id = ?", 1).build()
        self.assertEqual(sql, "DELETE FROM users WHERE id = ?")
        self.assertEqual(params, [1])

    def test_distinct(self):
        sql, _ = SQLBuilder("users").select("email").distinct().build()
        self.assertIn("DISTINCT", sql)

    def test_where_in(self):
        sql, params = SQLBuilder("users").select("*").where_in("id", [1, 2, 3]).build()
        self.assertIn("IN (?, ?, ?)", sql)
        self.assertEqual(params, [1, 2, 3])

    def test_where_between(self):
        sql, params = SQLBuilder("users").select("*").where_between("age", 20, 30).build()
        self.assertIn("BETWEEN ? AND ?", sql)
        self.assertEqual(params, [20, 30])

    def test_no_operation_raises(self):
        with self.assertRaises(DatabaseError):
            SQLBuilder("users").build()


class TestHandySQL(unittest.TestCase):
    """Tests for the HandySQL class"""

    def setUp(self):
        self.db = HandySQL(db_type="sqlite", database=":memory:")
        self.db.connect()
        self.db.create_table("users", {
            "id":    "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name":  "TEXT NOT NULL",
            "email": "TEXT UNIQUE",
            "age":   "INTEGER",
        })

    def tearDown(self):
        self.db.disconnect()

    # --- table helpers ---------------------------------------------------
    def test_table_exists(self):
        self.assertTrue(self.db.table_exists("users"))
        self.assertFalse(self.db.table_exists("nonexistent"))

    def test_quick_table(self):
        self.db.quick_table("posts", "title", "body")
        self.assertTrue(self.db.table_exists("posts"))
        self.assertIn("id", self.db.get_columns("posts"))
        self.assertIn("title", self.db.get_columns("posts"))

    def test_smart_table(self):
        self.db.smart_table("products", name="x", price=10, rating=4.5, active=True)
        cols = self.db.get_columns("products")
        self.assertIn("name", cols)
        self.assertIn("price", cols)

    def test_drop_table(self):
        self.db.drop_table("users")
        self.assertFalse(self.db.table_exists("users"))

    def test_get_columns(self):
        cols = self.db.get_columns("users")
        self.assertIn("id", cols)
        self.assertIn("name", cols)
        self.assertIn("email", cols)

    def test_column_exists(self):
        self.assertTrue(self.db.column_exists("users", "name"))
        self.assertFalse(self.db.column_exists("users", "phone"))

    # --- insert ----------------------------------------------------------
    def test_insert_row(self):
        self.db.insert_row("users", name="Alice", email="alice@test.com", age=25)
        user = self.db.fetch_one("users", name="Alice")
        self.assertIsNotNone(user)
        self.assertEqual(user["age"], 25)

    def test_add(self):
        self.db.add("users", name="Bob", email="bob@test.com", age=30)
        self.assertEqual(self.db.count("users"), 1)

    def test_insert_many(self):
        self.db.insert_many("users", [
            {"name": "Alice", "email": "a@test.com", "age": 25},
            {"name": "Bob",   "email": "b@test.com", "age": 30},
        ])
        self.assertEqual(self.db.count("users"), 2)

    def test_add_many(self):
        self.db.add_many("users",
            {"name": "Alice", "email": "a@test.com", "age": 25},
            {"name": "Bob",   "email": "b@test.com", "age": 30},
        )
        self.assertEqual(self.db.count("users"), 2)

    # --- select / fetch --------------------------------------------------
    def _seed(self):
        self.db.insert_many("users", [
            {"name": "Alice",   "email": "alice@test.com",   "age": 25},
            {"name": "Bob",     "email": "bob@test.com",     "age": 30},
            {"name": "Charlie", "email": "charlie@test.com", "age": 25},
        ])

    def test_fetch_all(self):
        self._seed()
        self.assertEqual(len(self.db.fetch_all("users")), 3)

    def test_fetch_one(self):
        self._seed()
        user = self.db.fetch_one("users", name="Alice")
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Alice")

    def test_find(self):
        self._seed()
        self.assertIsNotNone(self.db.find("users", name="Bob"))
        self.assertIsNone(self.db.find("users", name="Nobody"))

    def test_find_by_id(self):
        self._seed()
        user = self.db.find_by_id("users", 1)
        self.assertIsNotNone(user)

    def test_find_all(self):
        self._seed()
        self.assertEqual(len(self.db.find_all("users", age=25)), 2)

    def test_get_all(self):
        self._seed()
        rows = self.db.get_all("users", order_by="name ASC")
        self.assertEqual(rows[0]["name"], "Alice")

    def test_get_by_ids(self):
        self._seed()
        rows = self.db.get_by_ids("users", [1, 3])
        self.assertEqual(len(rows), 2)

    def test_first_last(self):
        self._seed()
        self.assertIsNotNone(self.db.first("users"))
        self.assertIsNotNone(self.db.last("users"))

    def test_latest_oldest(self):
        self._seed()
        self.assertIsNotNone(self.db.latest("users"))
        self.assertIsNotNone(self.db.oldest("users"))

    def test_pluck(self):
        self._seed()
        names = self.db.pluck("users", "name")
        self.assertEqual(len(names), 3)
        self.assertIn("Alice", names)

    def test_distinct_values(self):
        self._seed()
        ages = self.db.distinct_values("users", "age")
        self.assertEqual(sorted(ages), [25, 30])

    def test_search(self):
        self._seed()
        results = self.db.search("users", "name", "li")  # Alice, Charlie
        self.assertEqual(len(results), 2)

    def test_exists(self):
        self._seed()
        self.assertTrue(self.db.exists("users", name="Alice"))
        self.assertFalse(self.db.exists("users", name="Ghost"))

    def test_chunk(self):
        self._seed()
        chunks = list(self.db.chunk("users", size=2))
        self.assertEqual(len(chunks), 2)   # 2 chunks for 3 rows

    # --- update ----------------------------------------------------------
    def test_update_row(self):
        self._seed()
        self.db.update_row("users", {"age": 99}, name="Alice")
        self.assertEqual(self.db.find("users", name="Alice")["age"], 99)

    def test_change(self):
        self._seed()
        self.db.change("users", 1, age=50)
        self.assertEqual(self.db.find_by_id("users", 1)["age"], 50)

    def test_change_where(self):
        self._seed()
        self.db.change_where("users", {"age": 99}, name="Bob")
        self.assertEqual(self.db.find("users", name="Bob")["age"], 99)

    def test_increment_decrement(self):
        self._seed()
        self.db.increment("users", 1, "age")
        self.assertEqual(self.db.find_by_id("users", 1)["age"], 26)
        self.db.decrement("users", 1, "age", 6)
        self.assertEqual(self.db.find_by_id("users", 1)["age"], 20)

    def test_toggle(self):
        self.db.quick_table("flags", "active")
        self.db.add("flags", active="0")
        self.db.toggle("flags", 1, "active")
        self.assertEqual(int(self.db.find_by_id("flags", 1)["active"]), 1)
        self.db.toggle("flags", 1, "active")
        self.assertEqual(int(self.db.find_by_id("flags", 1)["active"]), 0)

    def test_update_or_create(self):
        row, created = self.db.update_or_create(
            "users",
            find_by={"email": "new@test.com"},
            defaults={"name": "New", "age": 20},
        )
        self.assertTrue(created)
        row2, created2 = self.db.update_or_create(
            "users",
            find_by={"email": "new@test.com"},
            defaults={"name": "Updated", "age": 21},
        )
        self.assertFalse(created2)

    def test_find_or_create(self):
        row, created = self.db.find_or_create(
            "users", name="NewUser", email="nu@test.com", age=20
        )
        self.assertTrue(created)
        row2, created2 = self.db.find_or_create(
            "users", name="NewUser", email="nu@test.com", age=20
        )
        self.assertFalse(created2)

    def test_clone_row(self):
        self._seed()
        self.db.clone_row("users", 1, name="Alice Clone", email="clone@test.com")
        self.assertEqual(self.db.count("users"), 4)
        clone = self.db.find("users", name="Alice Clone")
        self.assertIsNotNone(clone)
        self.assertEqual(clone["age"], 25)  # copied from original

    # --- delete ----------------------------------------------------------
    def test_delete_row(self):
        self._seed()
        self.db.delete_row("users", name="Alice")
        self.assertIsNone(self.db.find("users", name="Alice"))

    def test_remove(self):
        self._seed()
        self.db.remove("users", 1)
        self.assertIsNone(self.db.find_by_id("users", 1))

    def test_remove_where(self):
        self._seed()
        self.db.remove_where("users", age=25)
        self.assertEqual(self.db.count("users"), 1)

    def test_delete_requires_filter(self):
        with self.assertRaises(DatabaseError):
            self.db.delete_row("users")

    def test_delete_all_requires_confirm(self):
        self._seed()
        with self.assertRaises(DatabaseError):
            self.db.delete_all("users")
        self.db.delete_all("users", confirm=True)
        self.assertEqual(self.db.count("users"), 0)

    # --- aggregates ------------------------------------------------------
    def test_count(self):
        self._seed()
        self.assertEqual(self.db.count("users"), 3)
        self.assertEqual(self.db.count("users", age=25), 2)

    def test_sum_avg_min_max(self):
        self._seed()
        self.assertEqual(self.db.sum("users", "age"), 80)
        self.assertAlmostEqual(self.db.avg("users", "age"), 80 / 3, places=2)
        self.assertEqual(self.db.min("users", "age"), 25)
        self.assertEqual(self.db.max("users", "age"), 30)

    # --- pagination ------------------------------------------------------
    def test_paginate(self):
        for i in range(10):
            self.db.add("users", name=f"User{i}", email=f"u{i}@test.com", age=20 + i)
        result = self.db.paginate("users", page=1, per_page=3)
        self.assertEqual(result['total'], 10)
        self.assertEqual(result['pages'], 4)
        self.assertEqual(len(result['data']), 3)

    # --- copy / truncate -------------------------------------------------
    def test_copy_table(self):
        self._seed()
        self.db.copy_table("users", "users_bak")
        self.assertTrue(self.db.table_exists("users_bak"))
        self.assertEqual(self.db.count("users_bak"), 3)

    def test_truncate(self):
        self._seed()
        self.db.truncate("users")
        self.assertEqual(self.db.count("users"), 0)


class TestContextManager(unittest.TestCase):
    def test_with_statement(self):
        with HandySQL(db_type="sqlite", database=":memory:") as db:
            db.quick_table("t", "val")
            db.add("t", val="x")
            self.assertEqual(db.count("t"), 1)


def run_tests():
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in (TestSQLBuilder, TestHandySQL, TestContextManager):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 70)
    print("HandySQL – Unit Tests")
    print("=" * 70)
    success = run_tests()
    print("\n" + ("All tests passed!" if success else "Some tests FAILED!"))
