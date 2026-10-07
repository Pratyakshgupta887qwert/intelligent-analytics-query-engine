import re


# ==================================================
# ALLOWED TABLES
# ==================================================

ALLOWED_TABLES = {
    "sales",
    "targets",
}


# ==================================================
# SQL VALIDATOR
# ==================================================

def validate_sql(sql: str) -> str:
    """
    Validate generated SQL before execution.

    Supports:
    - SELECT queries
    - WITH / CTE queries
    - EXTRACT(YEAR FROM order_date)
    - JOIN operations
    - Multiple CTEs

    Allows only:
    - sales
    - targets
    - CTEs defined inside the query

    Blocks dangerous SQL operations.
    """

    # --------------------------------------------------
    # 1. EMPTY SQL CHECK
    # --------------------------------------------------

    if not sql or not sql.strip():
        raise ValueError(
            "SQL query cannot be empty."
        )

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
    # 3. BLOCK DANGEROUS SQL OPERATIONS
    # --------------------------------------------------

    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "truncate",
        "replace",
        "attach",
        "detach",
        "copy",
    ]

    for keyword in forbidden_keywords:

        pattern = rf"\b{keyword}\b"

        if re.search(
            pattern,
            normalized_sql
        ):
            raise ValueError(
                f"Forbidden SQL operation: "
                f"{keyword}"
            )

    # --------------------------------------------------
    # 4. FIND CTE NAMES
    # --------------------------------------------------
    #
    # Example:
    #
    # WITH yearly_revenue AS (...)
    #
    # yearly_revenue is a temporary query,
    # not a physical database table.
    #
    # --------------------------------------------------

    cte_names = set(
        re.findall(
            r"\bwith\s+"
            r"([a-zA-Z_][a-zA-Z0-9_]*)"
            r"\s+as\s*\(",
            normalized_sql,
        )
    )

    # --------------------------------------------------
    # 5. FIND ADDITIONAL CTE NAMES
    # --------------------------------------------------
    #
    # Example:
    #
    # WITH yearly_revenue AS (...),
    #      yearly_comparison AS (...)
    #
    # --------------------------------------------------

    additional_ctes = re.findall(
        r",\s*"
        r"([a-zA-Z_][a-zA-Z0-9_]*)"
        r"\s+as\s*\(",
        normalized_sql,
    )

    cte_names.update(
        additional_ctes
    )

    # --------------------------------------------------
    # 6. FIND FROM / JOIN REFERENCES
    # --------------------------------------------------

    table_pattern = re.compile(
        r"\b(from|join)\s+"
        r"([a-zA-Z_][a-zA-Z0-9_]*)",
        re.IGNORECASE,
    )

    for match in table_pattern.finditer(
        normalized_sql
    ):

        keyword = match.group(1)
        table_name = match.group(2)

        # --------------------------------------------------
        # Ignore FROM inside EXTRACT(...)
        # --------------------------------------------------

        preceding_text = normalized_sql[
            max(0, match.start() - 100):
            match.start()
        ]

        extract_match = re.search(
            r"extract\s*\([^)]*$",
            preceding_text,
            re.IGNORECASE,
        )

        if extract_match:
            continue

        # --------------------------------------------------
        # Allow approved physical tables
        # --------------------------------------------------

        if table_name in ALLOWED_TABLES:
            continue

        # --------------------------------------------------
        # Allow CTE tables
        # --------------------------------------------------

        if table_name in cte_names:
            continue

        # --------------------------------------------------
        # Reject unknown tables
        # --------------------------------------------------

        raise ValueError(
            f"Table '{table_name}' is not allowed."
        )

    # --------------------------------------------------
    # 7. RETURN VALIDATED SQL
    # --------------------------------------------------

    return sql