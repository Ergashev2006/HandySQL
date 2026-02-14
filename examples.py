"""
HandySQL - Usage Examples (English)
"""

from HandySQL import HandySQL, create_connection, sql_builder


def example_1_quick_table():
    print("\n=== Example 1: Quick table creation ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("users", "name", "email", "phone")
        print("Created 'users' table (id, name, email, phone)")
        db.add("users", name="Alice", email="alice@example.com", phone="+1-555-0101")
        print("Alice inserted")


def example_2_smart_table():
    print("\n=== Example 2: Smart table ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.smart_table("products",
            name="Phone",
            price=1500,
            rating=4.5,
            in_stock=True
        )
        print("'products' table created with auto-detected types")
        print("  name: TEXT  |  price: INTEGER  |  rating: REAL  |  in_stock: INTEGER")


def example_3_insert_and_find():
    print("\n=== Example 3: Insert & find ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("students", "name", "age", "grade")
        db.add("students", name="Alice",   age="18", grade="A")
        db.add("students", name="Bob",     age="19", grade="B")
        db.add("students", name="Charlie", age="18", grade="A")
        print("3 students inserted\n")

        alice = db.find("students", name="Alice")
        print(f"Found Alice: {alice}\n")

        student = db.find_by_id("students", 1)
        print(f"ID=1: {student}\n")

        top = db.find_all("students", grade="A")
        print(f"A-grade students ({len(top)}):")
        for s in top:
            print(f"  - {s['name']}")


def example_4_update():
    print("\n=== Example 4: Update ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("employees", "name", "position", "salary")
        db.add("employees", name="Alice", position="Developer", salary="5000")
        db.add("employees", name="Bob",   position="Manager",   salary="4000")

        # Update by ID
        db.change("employees", 1, name="Alice Smith", salary="5500")
        alice = db.find_by_id("employees", 1)
        print(f"Updated Alice: {alice['name']} – ${alice['salary']}\n")

        # Conditional update
        db.change_where("employees", {"position": "Senior Manager"}, name="Bob")
        bob = db.find("employees", name="Bob")
        print(f"Bob's new position: {bob['position']}")


def example_5_delete():
    print("\n=== Example 5: Delete ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("tasks", "title", "status")
        db.add("tasks", title="Task 1", status="done")
        db.add("tasks", title="Task 2", status="done")
        db.add("tasks", title="Task 3", status="pending")
        print(f"{db.count('tasks')} tasks created")

        db.remove("tasks", 1)
        print("Task 1 removed")

        db.remove_where("tasks", status="done")
        print("All completed tasks removed")
        print(f"Remaining: {db.count('tasks')} task(s)")


def example_6_bulk_insert():
    print("\n=== Example 6: Bulk insert ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("cities", "name", "country", "population")
        db.add_many("cities",
            {"name": "New York", "country": "USA",   "population": "8300000"},
            {"name": "London",   "country": "UK",    "population": "9000000"},
            {"name": "Tokyo",    "country": "Japan", "population": "13960000"}
        )
        cities = db.get_all("cities", order_by="population DESC")
        print("Cities by population:")
        for c in cities:
            print(f"  {c['name']}: {c['population']}")


def example_7_exists():
    print("\n=== Example 7: Existence check ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("accounts", "username", "email")
        username = "alice123"
        if db.exists("accounts", username=username):
            print(f"Username '{username}' is already taken")
        else:
            db.add("accounts", username=username, email="alice@example.com")
            print(f"Account created: {username}")
        # Second attempt
        if db.exists("accounts", username=username):
            print(f"Username '{username}' is already taken!")


def example_8_search():
    print("\n=== Example 8: Search ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("books", "title", "author", "year")
        db.add_many("books",
            {"title": "Python Programming",   "author": "Alice",   "year": "2020"},
            {"title": "Advanced Python",      "author": "Bob",     "year": "2021"},
            {"title": "JavaScript Basics",    "author": "Charlie", "year": "2019"},
            {"title": "Python and AI",        "author": "Dave",    "year": "2022"}
        )
        results = db.search("books", "title", "Python")
        print(f"Results for 'Python' ({len(results)} found):")
        for b in results:
            print(f"  - {b['title']} ({b['year']})")


def example_9_statistics():
    print("\n=== Example 9: Statistics ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("orders", "customer", "amount")
        db.add_many("orders",
            {"customer": "Alice",   "amount": "100"},
            {"customer": "Bob",     "amount": "250"},
            {"customer": "Charlie", "amount": "150"},
            {"customer": "Dave",    "amount": "300"}
        )
        print(f"Count   : {db.count('orders')}")
        print(f"Total   : ${db.sum('orders', 'amount'):.2f}")
        print(f"Average : ${db.avg('orders', 'amount'):.2f}")
        print(f"Min     : ${db.min('orders', 'amount')}")
        print(f"Max     : ${db.max('orders', 'amount')}")


def example_10_pagination():
    print("\n=== Example 10: Pagination ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("items", "name")
        for i in range(1, 16):
            db.add("items", name=f"Item {i}")
        page = db.paginate("items", page=1, per_page=5)
        print(f"Page {page['page']} of {page['pages']}  (total: {page['total']})")
        for item in page['data']:
            print(f"  - {item['name']}")


def example_11_counters():
    print("\n=== Example 11: increment / decrement / toggle ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.smart_table("posts", title="Post", views=0, published=False)
        db.add("posts", title="Hello World", views="0", published="0")

        db.increment("posts", 1, "views")
        db.increment("posts", 1, "views")
        db.increment("posts", 1, "views")
        db.toggle("posts", 1, "published")

        post = db.find_by_id("posts", 1)
        print(f"Views     : {post['views']}")
        print(f"Published : {post['published']}")


def example_12_upsert():
    print("\n=== Example 12: update_or_create / find_or_create ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("user_prefs", "user_id", "theme", "language")

        pref, created = db.update_or_create(
            "user_prefs",
            find_by={"user_id": "1"},
            defaults={"theme": "dark", "language": "en"},
        )
        print(f"{'Created' if created else 'Updated'}: {pref}")

        pref, created = db.update_or_create(
            "user_prefs",
            find_by={"user_id": "1"},
            defaults={"theme": "light"},
        )
        print(f"{'Created' if created else 'Updated'}: {pref}")


def example_13_sql_builder():
    print("\n=== Example 13: SQL Builder ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        db.quick_table("catalog", "name", "price", "category")
        db.add_many("catalog",
            {"name": "Laptop",     "price": "1200", "category": "electronics"},
            {"name": "Phone",      "price": "800",  "category": "electronics"},
            {"name": "T-Shirt",    "price": "30",   "category": "clothing"},
            {"name": "Headphones", "price": "150",  "category": "electronics"},
        )

        # WHERE IN
        q = (db.query("catalog")
               .select("*")
               .where_in("name", ["Laptop", "Phone"])
               .order_by("price", "DESC"))
        sql, params = q.build()
        for r in db.execute(sql, params):
            print(f"  {r['name']} – ${r['price']}")

        # WHERE BETWEEN
        q2 = db.query("catalog").select("*").where_between("price", 100, 1000)
        sql2, params2 = q2.build()
        results2 = db.execute(sql2, params2)
        print(f"\n$100–$1000 range ({len(results2)} items):")
        for r in results2:
            print(f"  {r['name']} – ${r['price']}")


def example_14_transactions():
    print("\n=== Example 14: Transactions ===\n")
    db = create_connection("sqlite", database="demo.db")
    db.connect()
    try:
        db.begin_transaction()
        db.quick_table("audit_log", "action", "user_id")
        db.add("audit_log", action="login",  user_id="1")
        db.add("audit_log", action="update", user_id="1")
        db.commit()
        print("Transaction committed successfully")
    except Exception as e:
        db.rollback()
        print(f"Transaction rolled back: {e}")
    finally:
        db.disconnect()


def example_15_context_manager():
    print("\n=== Example 15: Context manager ===\n")
    with HandySQL(db_type="sqlite", database="demo.db") as db:
        tables = db.get_tables()
        print(f"Tables in database ({len(tables)}):")
        for t in tables:
            print(f"  - {t}")
    print("Connection closed automatically")


def run_all():
    print("=" * 70)
    print("HandySQL – Usage Examples")
    print("=" * 70)

    fns = [
        example_1_quick_table, example_2_smart_table,
        example_3_insert_and_find, example_4_update, example_5_delete,
        example_6_bulk_insert, example_7_exists, example_8_search,
        example_9_statistics, example_10_pagination, example_11_counters,
        example_12_upsert, example_13_sql_builder, example_14_transactions,
        example_15_context_manager,
    ]

    for fn in fns:
        try:
            fn()
        except Exception as e:
            print(f"\nERROR in {fn.__name__}: {e}")

    print("\n" + "=" * 70)
    print("All examples finished!")
    print("=" * 70)


if __name__ == "__main__":
    run_all()
