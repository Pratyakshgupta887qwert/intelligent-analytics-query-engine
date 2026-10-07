from app.models.query_plan import QueryPlan
from app.services.sql_generator import generate_sql
from app.core.sql_validator import validate_sql


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

validated_sql = validate_sql(sql)


print("\n===== VALIDATED SQL =====")
print(validated_sql)