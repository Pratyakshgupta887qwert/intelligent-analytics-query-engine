from app.query_executor import execute_query


sql = """
SELECT
    SUM(
        quantity * unit_price * (1 - discount)
    ) AS total_sales
FROM sales
WHERE country = 'India'
  AND strftime(order_date, '%Y-%m') = '2024-03'
"""


result = execute_query(sql)

print("\n===== QUERY RESULT =====")
print(result)