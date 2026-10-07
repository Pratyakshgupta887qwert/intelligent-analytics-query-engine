from app.services.genai_service import parse_natural_language_query
from app.services.query_service import execute_query_plan


query = "Sales contribution % by category"

plan = parse_natural_language_query(query)

response = execute_query_plan(plan)


print("\n===== USER QUERY =====")
print(query)

print("\n===== QUERY PLAN =====")
print(response["query_plan"])

print("\n===== GENERATED SQL =====")
print(response["generated_sql"])

print("\n===== RESULT =====")
print(response["result"])