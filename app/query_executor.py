from app.database import get_connection


def execute_query(sql: str):
    """
    Execute a read-only analytical SQL query.

    Supports:
    - SELECT queries
    - WITH / CTE queries

    Only read operations are allowed.
    """

    connection = get_connection()

    try:

        # --------------------------------------------------
        # 1. NORMALIZE SQL
        # --------------------------------------------------

        normalized_sql = sql.strip().lower()

        # --------------------------------------------------
        # 2. ALLOW SELECT AND WITH QUERIES
        # --------------------------------------------------

        if not (
            normalized_sql.startswith("select")
            or normalized_sql.startswith("with")
        ):
            raise ValueError(
                "Only SELECT queries are allowed."
            )

        # --------------------------------------------------
        # 3. EXECUTE QUERY
        # --------------------------------------------------

        result = connection.execute(
            sql
        ).fetchdf()

        return result

    finally:

        connection.close()