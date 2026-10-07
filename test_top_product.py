from app.services.genai_service import parse_natural_language_query


query = "Top product in each region"

plan = parse_natural_language_query(query)


print("\n===== USER QUERY =====")
print(query)

print("\n===== QUERY PLAN =====")
print(plan.model_dump())