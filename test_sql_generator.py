from app.models.query_plan import QueryPlan
from app.services.sql_generator import generate_sql


plan = QueryPlan(
    metric="revenue",
    aggregation="sum",
    group_by=[],
    filters={
        "country": "India"
    },
    time_range="2024-03"
)


sql = generate_sql(plan)


print("\n===== GENERATED SQL =====")
print(sql)