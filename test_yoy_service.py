from app.services.genai_service import parse_natural_language_query
from app.services.query_service import execute_query_plan


# --------------------------------------------------
# TEST QUERY
# --------------------------------------------------

query = "YoY growth in revenue"


# --------------------------------------------------
# STEP 1: CONVERT NATURAL LANGUAGE
# INTO QUERY PLAN
# --------------------------------------------------

plan = parse_natural_language_query(query)


# --------------------------------------------------
# STEP 2: EXECUTE QUERY PLAN
# --------------------------------------------------

response = execute_query_plan(plan)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print("\n===== USER QUERY =====")
print(query)

print("\n===== QUERY PLAN =====")
print(response["query_plan"])

print("\n===== GENERATED SQL =====")
print(response["generated_sql"])

print("\n===== RESULT =====")
print(response["result"])