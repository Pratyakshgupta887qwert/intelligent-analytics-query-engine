from app.models.query_plan import QueryPlan
from app.services.sql_generator import generate_sql
from app.core.sql_validator import validate_sql
from app.query_executor import execute_query


def execute_query_plan(plan: QueryPlan):
    """
    Execute a complete structured query plan.

    Pipeline:
        QueryPlan
        -> SQL Generator
        -> SQL Validator
        -> SQL Executor
        -> Result
    """

    # Step 1: Generate SQL
    sql = generate_sql(plan)

    # Step 2: Validate generated SQL
    validated_sql = validate_sql(sql)

    # Step 3: Execute SQL
    result = execute_query(validated_sql)

    return {
        "query_plan": plan.model_dump(),
        "generated_sql": validated_sql,
        "result": result,
    }