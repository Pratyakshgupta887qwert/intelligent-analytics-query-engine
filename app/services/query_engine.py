from app.services.genai_service import parse_natural_language_query
from app.services.query_service import execute_query_plan


def calculate_confidence(query_plan):
    """
    Calculate a transparent confidence score based on
    how completely the natural-language query was mapped
    into a structured QueryPlan.

    Score range: 0.0 - 1.0
    """

    score = 0.70

    # Metric identified
    if query_plan.metric:
        score += 0.05

    # Aggregation identified
    if query_plan.aggregation:
        score += 0.05

    # Grouping identified
    if query_plan.group_by:
        score += 0.05

    # Filters identified
    if query_plan.filters:
        score += 0.05

    # Time range identified
    if query_plan.time_range:
        score += 0.05

    # Ranking identified
    if query_plan.ranking:
        score += 0.05

    # Comparison identified
    if query_plan.comparison:
        score += 0.05

    return min(round(score, 2), 1.0)


def generate_explanation(query_plan):
    """
    Generate a human-readable explanation of how
    the system interpreted the user's query.
    """

    metric_names = {
        "revenue": "revenue",
        "profit": "profit",
        "orders": "number of orders",
        "avg_order_value": "average order value",
    }

    metric_text = metric_names.get(
        query_plan.metric,
        query_plan.metric,
    )

    explanation_parts = [
        f"The system interpreted the requested metric as {metric_text}."
    ]

    # --------------------------------------------------
    # GROUPING
    # --------------------------------------------------

    if query_plan.group_by:

        dimensions = ", ".join(
            query_plan.group_by
        )

        explanation_parts.append(
            f"The result is grouped by {dimensions}."
        )

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    if query_plan.filters:

        filter_text = ", ".join(
            f"{column} = {value}"
            for column, value
            in query_plan.filters.items()
        )

        explanation_parts.append(
            f"The query applies the filter {filter_text}."
        )

    # --------------------------------------------------
    # TIME RANGE
    # --------------------------------------------------

    if query_plan.time_range:

        explanation_parts.append(
            f"The query is restricted to "
            f"{query_plan.time_range}."
        )

    # --------------------------------------------------
    # RANKING
    # --------------------------------------------------

    if query_plan.ranking:

        ranking = query_plan.ranking

        direction = ranking.get(
            "direction",
            "desc",
        )

        limit = ranking.get(
            "limit",
        )

        partition_by = ranking.get(
            "partition_by",
        )

        rank_dimension = ranking.get(
            "rank_dimension",
        )

        if partition_by and rank_dimension:

            direction_text = (
                "highest"
                if direction == "desc"
                else "lowest"
            )

            explanation_parts.append(
                f"The system ranks {rank_dimension} "
                f"within each {partition_by} and returns "
                f"the top {limit} based on the "
                f"{direction_text} metric value."
            )

        elif limit:

            direction_text = (
                "highest"
                if direction == "desc"
                else "lowest"
            )

            explanation_parts.append(
                f"The system returns the top {limit} "
                f"results based on the "
                f"{direction_text} metric value."
            )

    # --------------------------------------------------
    # COMPARISON
    # --------------------------------------------------

    if query_plan.comparison:

        comparison_type = query_plan.comparison.get(
            "type"
        )

        if comparison_type == "target":

            explanation_parts.append(
                "The system compares actual revenue "
                "against the corresponding regional target."
            )

        elif comparison_type == "contribution_percentage":

            explanation_parts.append(
                "The system calculates each group's "
                "percentage contribution to total revenue."
            )

        elif comparison_type == "yoy":

            explanation_parts.append(
                "The system compares revenue for each year "
                "with the previous year and calculates "
                "the year-over-year growth percentage."
            )

    return " ".join(
        explanation_parts
    )


def process_natural_language_query(
    user_query: str
):
    """
    Complete analytics query pipeline:

        Natural language
              ↓
        QueryPlan
              ↓
        SQL generation
              ↓
        SQL validation
              ↓
        SQL execution
              ↓
        Confidence score
              ↓
        Explanation
    """

    if not user_query or not user_query.strip():

        raise ValueError(
            "Query cannot be empty."
        )

    # --------------------------------------------------
    # 1. PARSE NATURAL LANGUAGE
    # --------------------------------------------------

    query_plan = parse_natural_language_query(
        user_query
    )

    # --------------------------------------------------
    # 2. EXECUTE QUERY PLAN
    # --------------------------------------------------

    execution_result = execute_query_plan(
        query_plan
    )

    # --------------------------------------------------
    # 3. CONFIDENCE SCORE
    # --------------------------------------------------

    confidence_score = calculate_confidence(
        query_plan
    )

    # --------------------------------------------------
    # 4. EXPLANATION
    # --------------------------------------------------

    explanation = generate_explanation(
        query_plan
    )

    # --------------------------------------------------
    # 5. FINAL RESPONSE
    # --------------------------------------------------

    return {
        "query": user_query,

        "generated_logic": execution_result[
            "generated_sql"
        ],

        "result": execution_result[
            "result"
        ].to_dict(
            orient="records"
        ),

        "confidence_score": confidence_score,

        "explanation": explanation,
    }