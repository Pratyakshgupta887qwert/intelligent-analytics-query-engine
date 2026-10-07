from app.services.genai_service import parse_natural_language_query


query = "Which region missed its target in Feb?"


plan = parse_natural_language_query(query)


print("\n===== USER QUERY =====")
print(query)

print("\n===== GENERATED QUERY PLAN =====")
print(plan.model_dump())