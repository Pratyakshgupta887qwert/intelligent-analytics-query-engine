from app.services.genai_service import parse_natural_language_query


query = "YoY growth in revenue"

plan = parse_natural_language_query(query)


print("\n===== USER QUERY =====")
print(query)

print("\n===== QUERY PLAN =====")
print(plan.model_dump())