from app.database import create_database, get_connection


# Create database
create_database()

# Connect to database
connection = get_connection()

print("\n===== TABLES =====")

tables = connection.execute(
    "SHOW TABLES"
).fetchall()

print(tables)


print("\n===== SALES SAMPLE =====")

sales = connection.execute("""
    SELECT *
    FROM sales
    LIMIT 3
""").fetchdf()

print(sales)


print("\n===== TARGETS SAMPLE =====")

targets = connection.execute("""
    SELECT *
    FROM targets
    LIMIT 3
""").fetchdf()

print(targets)


connection.close()