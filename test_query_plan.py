from app.models.query_plan import QueryPlan


plan = QueryPlan(
    metric="revenue",
    aggregation="sum",
    group_by=[],
    filters={
        "country": "India"
    },
    time_range="2024-03"
)


print("\n===== QUERY PLAN =====")
print(plan.model_dump())