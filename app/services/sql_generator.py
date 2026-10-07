from app.models.query_plan import QueryPlan


# --------------------------------------------------
# BUSINESS METRICS
# --------------------------------------------------

METRIC_EXPRESSIONS = {
    "revenue": "quantity * unit_price * (1 - discount)",

    "profit": "profit",

    "orders": "order_id",

    "avg_order_value": (
        "quantity * unit_price * (1 - discount)"
    ),
}


# --------------------------------------------------
# ALLOWED DIMENSIONS
# --------------------------------------------------

ALLOWED_DIMENSIONS = {
    "region",
    "country",
    "city",
    "customer_id",
    "customer_segment",
    "product_category",
    "product_subcategory",
    "product_name",
    "order_date",
}


# ==================================================
# MAIN SQL GENERATOR
# ==================================================

def generate_sql(plan: QueryPlan) -> str:
    """
    Convert a structured QueryPlan into executable
    DuckDB SQL.

    Supports:

    - Revenue
    - Profit
    - Orders
    - Average Order Value
    - Filters
    - Grouping
    - Top-N / Bottom-N
    - Target comparison
    - Contribution percentage
    - Top product in each region
    - Year-over-year growth
    """

    # --------------------------------------------------
    # 1. VALIDATE METRIC
    # --------------------------------------------------

    if plan.metric not in METRIC_EXPRESSIONS:
        raise ValueError(
            f"Unsupported metric: {plan.metric}"
        )

    # --------------------------------------------------
    # 2. VALIDATE AGGREGATION
    # --------------------------------------------------

    allowed_aggregations = {
        "sum",
        "count",
        "avg",
    }

    if plan.aggregation not in allowed_aggregations:
        raise ValueError(
            f"Unsupported aggregation: "
            f"{plan.aggregation}"
        )

    # --------------------------------------------------
    # 3. VALIDATE GROUP BY
    # --------------------------------------------------

    for dimension in plan.group_by:

        if dimension not in ALLOWED_DIMENSIONS:
            raise ValueError(
                f"Unsupported dimension: "
                f"{dimension}"
            )

    # --------------------------------------------------
    # 4. SPECIAL COMPARISON QUERIES
    # --------------------------------------------------

    # Target comparison
    if (
        plan.comparison
        and plan.comparison.get("type")
        == "target"
    ):
        return generate_target_comparison_sql(plan)

    # Contribution percentage
    if (
        plan.comparison
        and plan.comparison.get("type")
        == "contribution_percentage"
    ):
        return generate_contribution_percentage_sql(
            plan
        )

    # Year-over-year growth
    if (
        plan.comparison
        and plan.comparison.get("type")
        == "yoy"
    ):
        return generate_yoy_sql(plan)

    # --------------------------------------------------
    # 5. SPECIAL PARTITIONED RANKING
    # --------------------------------------------------

    if (
        plan.ranking
        and plan.ranking.get("partition_by")
    ):
        return generate_partitioned_ranking_sql(
            plan
        )

    # --------------------------------------------------
    # 6. NORMAL QUERY
    # --------------------------------------------------

    metric_expression = METRIC_EXPRESSIONS[
        plan.metric
    ]

    select_parts = []

    # --------------------------------------------------
    # 7. GROUPING DIMENSIONS
    # --------------------------------------------------

    for dimension in plan.group_by:
        select_parts.append(dimension)

    # --------------------------------------------------
    # 8. AGGREGATION
    # --------------------------------------------------

    if plan.metric == "orders":

        aggregation_sql = (
            "COUNT(order_id)"
        )

    elif plan.metric == "avg_order_value":

        aggregation_sql = (
            "SUM("
            "quantity * unit_price * (1 - discount)"
            ") "
            "/ NULLIF(COUNT(order_id), 0)"
        )

    elif plan.aggregation == "sum":

        aggregation_sql = (
            f"SUM({metric_expression})"
        )

    elif plan.aggregation == "avg":

        aggregation_sql = (
            f"AVG({metric_expression})"
        )

    elif plan.aggregation == "count":

        aggregation_sql = (
            f"COUNT({metric_expression})"
        )

    else:

        raise ValueError(
            "Invalid aggregation"
        )

    # --------------------------------------------------
    # 9. RESULT ALIAS
    # --------------------------------------------------

    if plan.metric == "revenue":

        alias = "total_revenue"

    elif plan.metric == "avg_order_value":

        alias = "avg_order_value"

    else:

        alias = (
            f"{plan.aggregation}_"
            f"{plan.metric}"
        )

    select_parts.append(
        f"{aggregation_sql} AS {alias}"
    )

    # --------------------------------------------------
    # 10. SELECT
    # --------------------------------------------------

    sql = "SELECT\n    "

    sql += ",\n    ".join(
        select_parts
    )

    # --------------------------------------------------
    # 11. FROM
    # --------------------------------------------------

    sql += "\nFROM sales"

    # --------------------------------------------------
    # 12. WHERE CONDITIONS
    # --------------------------------------------------

    conditions = []

    for column, value in plan.filters.items():

        if column not in ALLOWED_DIMENSIONS:
            raise ValueError(
                f"Unsupported filter column: "
                f"{column}"
            )

        safe_value = (
            str(value)
            .replace("'", "''")
        )

        conditions.append(
            f"{column} = '{safe_value}'"
        )

    # --------------------------------------------------
    # 13. TIME RANGE
    # --------------------------------------------------

    if plan.time_range:

        conditions.append(
            "strftime(order_date, '%Y-%m') "
            f"= '{plan.time_range}'"
        )

    # --------------------------------------------------
    # 14. WHERE
    # --------------------------------------------------

    if conditions:

        sql += "\nWHERE\n    "

        sql += "\n    AND ".join(
            conditions
        )

    # --------------------------------------------------
    # 15. GROUP BY
    # --------------------------------------------------

    if plan.group_by:

        sql += "\nGROUP BY "

        sql += ", ".join(
            plan.group_by
        )

    # --------------------------------------------------
    # 16. GLOBAL RANKING
    # --------------------------------------------------

    if plan.ranking:

        direction = plan.ranking.get(
            "direction",
            "desc"
        )

        limit = plan.ranking.get(
            "limit"
        )

        if direction not in {
            "asc",
            "desc",
        }:

            raise ValueError(
                "Ranking direction must be "
                "'asc' or 'desc'."
            )

        if limit is not None:

            try:
                limit = int(limit)

            except (
                TypeError,
                ValueError,
            ):

                raise ValueError(
                    "Ranking limit must be "
                    "an integer."
                )

            if limit <= 0:

                raise ValueError(
                    "Ranking limit must be "
                    "greater than zero."
                )

            sql += (
                f"\nORDER BY {alias} "
                f"{direction.upper()}"
                f"\nLIMIT {limit}"
            )

    # --------------------------------------------------
    # 17. RETURN
    # --------------------------------------------------

    return sql + ";"


# ==================================================
# PARTITIONED RANKING
# ==================================================

def generate_partitioned_ranking_sql(
    plan: QueryPlan
) -> str:
    """
    Generate SQL for ranking within each group.

    Example:

        Top product in each region

    Logic:

        1. Calculate revenue for every
           region/product combination.

        2. Rank products separately
           inside each region.

        3. Keep the requested top N.
    """

    # --------------------------------------------------
    # 1. READ RANKING CONFIGURATION
    # --------------------------------------------------

    partition_by = plan.ranking.get(
        "partition_by"
    )

    rank_dimension = plan.ranking.get(
        "rank_dimension"
    )

    direction = plan.ranking.get(
        "direction",
        "desc"
    )

    limit = plan.ranking.get(
        "limit",
        1
    )

    # --------------------------------------------------
    # 2. VALIDATE CONFIGURATION
    # --------------------------------------------------

    if partition_by not in ALLOWED_DIMENSIONS:

        raise ValueError(
            f"Unsupported partition dimension: "
            f"{partition_by}"
        )

    if rank_dimension not in ALLOWED_DIMENSIONS:

        raise ValueError(
            f"Unsupported ranking dimension: "
            f"{rank_dimension}"
        )

    if direction not in {
        "asc",
        "desc",
    }:

        raise ValueError(
            "Ranking direction must be "
            "'asc' or 'desc'."
        )

    try:

        limit = int(limit)

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            "Ranking limit must be an integer."
        )

    if limit <= 0:

        raise ValueError(
            "Ranking limit must be "
            "greater than zero."
        )

    # --------------------------------------------------
    # 3. BUILD FILTER CONDITIONS
    # --------------------------------------------------

    conditions = []

    for column, value in plan.filters.items():

        if column not in ALLOWED_DIMENSIONS:

            raise ValueError(
                f"Unsupported filter column: "
                f"{column}"
            )

        safe_value = (
            str(value)
            .replace("'", "''")
        )

        conditions.append(
            f"{column} = '{safe_value}'"
        )

    # --------------------------------------------------
    # 4. TIME FILTER
    # --------------------------------------------------

    if plan.time_range:

        conditions.append(
            "strftime(order_date, '%Y-%m') "
            f"= '{plan.time_range}'"
        )

    # --------------------------------------------------
    # 5. WHERE CLAUSE
    # --------------------------------------------------

    where_clause = ""

    if conditions:

        where_clause = (
            "\nWHERE\n        "
            + "\n        AND ".join(
                conditions
            )
        )

    # --------------------------------------------------
    # 6. RANKING DIRECTION
    # --------------------------------------------------

    order_direction = (
        direction.upper()
    )

    # --------------------------------------------------
    # 7. GENERATE PARTITIONED QUERY
    # --------------------------------------------------

    sql = f"""
SELECT
    {partition_by},
    {rank_dimension},
    total_revenue

FROM (

    SELECT
        {partition_by},
        {rank_dimension},

        SUM(
            quantity
            * unit_price
            * (1 - discount)
        ) AS total_revenue,

        ROW_NUMBER() OVER (
            PARTITION BY {partition_by}

            ORDER BY
                SUM(
                    quantity
                    * unit_price
                    * (1 - discount)
                ) {order_direction}

        ) AS ranking

    FROM sales

    {where_clause}

    GROUP BY
        {partition_by},
        {rank_dimension}

) ranked_data

WHERE ranking <= {limit}

ORDER BY
    {partition_by},
    total_revenue DESC;
"""

    return sql.strip()


# ==================================================
# CONTRIBUTION PERCENTAGE
# ==================================================

def generate_contribution_percentage_sql(
    plan: QueryPlan
) -> str:
    """
    Generate SQL for contribution percentage.

    Example:

        Sales contribution % by category

    Logic:

        category revenue
        ---------------- × 100
        total revenue
    """

    # --------------------------------------------------
    # 1. VALIDATE GROUPING
    # --------------------------------------------------

    if len(plan.group_by) != 1:

        raise ValueError(
            "Contribution percentage requires exactly "
            "one grouping dimension."
        )

    dimension = plan.group_by[0]

    if dimension not in ALLOWED_DIMENSIONS:

        raise ValueError(
            f"Unsupported contribution dimension: "
            f"{dimension}"
        )

    # --------------------------------------------------
    # 2. FILTER CONDITIONS
    # --------------------------------------------------

    conditions = []

    for column, value in plan.filters.items():

        if column not in ALLOWED_DIMENSIONS:

            raise ValueError(
                f"Unsupported filter column: "
                f"{column}"
            )

        safe_value = (
            str(value)
            .replace("'", "''")
        )

        conditions.append(
            f"{column} = '{safe_value}'"
        )

    # --------------------------------------------------
    # 3. TIME FILTER
    # --------------------------------------------------

    if plan.time_range:

        conditions.append(
            "strftime(order_date, '%Y-%m') "
            f"= '{plan.time_range}'"
        )

    # --------------------------------------------------
    # 4. WHERE CLAUSE
    # --------------------------------------------------

    where_clause = ""

    if conditions:

        where_clause = (
            "\nWHERE\n    "
            + "\n    AND ".join(
                conditions
            )
        )

    # --------------------------------------------------
    # 5. SQL
    # --------------------------------------------------

    sql = f"""
SELECT
    {dimension},

    SUM(
        quantity
        * unit_price
        * (1 - discount)
    ) AS revenue,

    ROUND(

        SUM(
            quantity
            * unit_price
            * (1 - discount)
        )

        /

        NULLIF(

            SUM(
                SUM(
                    quantity
                    * unit_price
                    * (1 - discount)
                )
            ) OVER (),

            0
        )

        * 100,

        2

    ) AS contribution_percentage

FROM sales

{where_clause}

GROUP BY
    {dimension}

ORDER BY
    contribution_percentage DESC;
"""

    return sql.strip()


# ==================================================
# TARGET COMPARISON
# ==================================================

def generate_target_comparison_sql(
    plan: QueryPlan
) -> str:
    """
    Generate SQL for comparing actual revenue
    against regional monthly revenue targets.

    Example:

        Which region missed its target in Feb?

    Logic:

        Actual Revenue < Target Revenue
    """

    # --------------------------------------------------
    # 1. VALIDATE OPERATOR
    # --------------------------------------------------

    operator = plan.comparison.get(
        "operator",
        "below"
    )

    if operator not in {
        "below",
        "above",
    }:

        raise ValueError(
            "Unsupported target comparison "
            "operator."
        )

    # --------------------------------------------------
    # 2. DETERMINE SQL OPERATOR
    # --------------------------------------------------

    comparison_operator = "<"

    if operator == "above":

        comparison_operator = ">"

    # --------------------------------------------------
    # 3. VALIDATE TIME RANGE
    # --------------------------------------------------

    if not plan.time_range:

        raise ValueError(
            "Target comparison requires "
            "a time range."
        )

    month = plan.time_range

    # --------------------------------------------------
    # 4. GENERATE SQL
    # --------------------------------------------------

    sql = f"""
SELECT
    s.region,

    SUM(
        s.quantity
        * s.unit_price
        * (1 - s.discount)
    ) AS actual_revenue,

    t.target_revenue

FROM sales AS s

JOIN targets AS t

    ON s.region = t.region

    AND strftime(
        s.order_date,
        '%Y-%m'
    ) = t.month

WHERE
    t.month = '{month}'

GROUP BY
    s.region,
    t.target_revenue

HAVING

    SUM(
        s.quantity
        * s.unit_price
        * (1 - s.discount)
    ) {comparison_operator} t.target_revenue;
"""

    return sql.strip()


# ==================================================
# YEAR-OVER-YEAR GROWTH
# ==================================================

def generate_yoy_sql(
    plan: QueryPlan
) -> str:
    """
    Generate SQL for year-over-year revenue growth.

    Compares each year's revenue with
    the previous year's revenue.
    """

    # --------------------------------------------------
    # 1. VALIDATE METRIC
    # --------------------------------------------------

    if plan.metric != "revenue":

        raise ValueError(
            "YoY comparison currently supports "
            "revenue only."
        )

    # --------------------------------------------------
    # 2. BUILD FILTER CONDITIONS
    # --------------------------------------------------

    conditions = []

    for column, value in plan.filters.items():

        if column not in ALLOWED_DIMENSIONS:

            raise ValueError(
                f"Unsupported filter column: "
                f"{column}"
            )

        safe_value = (
            str(value)
            .replace("'", "''")
        )

        conditions.append(
            f"{column} = '{safe_value}'"
        )

    # --------------------------------------------------
    # 3. WHERE CLAUSE
    # --------------------------------------------------

    where_clause = ""

    if conditions:

        where_clause = (
            "\nWHERE\n        "
            + "\n        AND ".join(
                conditions
            )
        )

    # --------------------------------------------------
    # 4. GENERATE YOY SQL
    # --------------------------------------------------

    sql = f"""
WITH yearly_revenue AS (

    SELECT

        EXTRACT(
            YEAR FROM order_date
        ) AS year,

        SUM(
            quantity
            * unit_price
            * (1 - discount)
        ) AS revenue

    FROM sales

    {where_clause}

    GROUP BY
        EXTRACT(
            YEAR FROM order_date
        )
),

yearly_comparison AS (

    SELECT

        year,

        revenue AS current_revenue,

        LAG(revenue) OVER (
            ORDER BY year
        ) AS previous_revenue

    FROM yearly_revenue
)

SELECT

    year,

    current_revenue,

    previous_revenue,

    ROUND(

        (
            (
                current_revenue
                - previous_revenue
            )

            /

            NULLIF(
                previous_revenue,
                0
            )

        ) * 100,

        2

    ) AS yoy_growth_percentage

FROM yearly_comparison

WHERE
    previous_revenue IS NOT NULL

ORDER BY
    year;
"""

    return sql.strip()