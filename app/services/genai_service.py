import json
import re
from pathlib import Path

from app.models.query_plan import QueryPlan


# ==================================================
# PROJECT PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"


# ==================================================
# DATA DICTIONARY
# ==================================================

def load_data_dictionary():
    """
    Load and normalize the project's data dictionary.

    The supplied JSON file contains each line wrapped in
    double quotes and uses doubled quotation marks internally.
    """

    file_path = DATA_DIR / "data_dictionary.json"

    raw_text = file_path.read_text(
        encoding="utf-8-sig"
    )

    cleaned_lines = []

    for line in raw_text.splitlines():

        line = line.strip()

        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]

        line = line.replace('""', '"')

        cleaned_lines.append(line)

    cleaned_json = "\n".join(cleaned_lines)

    return json.loads(cleaned_json)


# ==================================================
# MOCK GENAI PROVIDER
# ==================================================

class MockGenAIProvider:
    """
    Free development-time GenAI provider.

    This does not call any paid API.

    It converts common natural-language analytics
    requests into a structured QueryPlan.
    """

    def generate_query_plan(
        self,
        user_query: str
    ) -> QueryPlan:

        query = user_query.lower().strip()

        # ==================================================
        # 1. DETERMINE METRIC
        # ==================================================

        # Target-related and sales-related questions
        # use revenue.

        if any(
            word in query
            for word in [
                "sales",
                "revenue",
                "income",
                "target",
                "targeted",
                "missed its target",
                "missed target",
            ]
        ):

            metric = "revenue"
            aggregation = "sum"

        # Profit-related questions.

        elif any(
            word in query
            for word in [
                "profit",
                "earnings",
            ]
        ):

            metric = "profit"
            aggregation = "sum"

        # Average order value.

        elif (
            "average order value" in query
            or "aov" in query
        ):

            metric = "avg_order_value"
            aggregation = "avg"

        # Order-related questions.

        elif "order" in query:

            metric = "orders"
            aggregation = "count"

        # Product ranking questions.

        elif (
            "top product" in query
            or "best product" in query
        ):

            metric = "revenue"
            aggregation = "sum"

        # Customer ranking questions.

        elif (
            "top customer" in query
            or "best customer" in query
            or "customers per region" in query
        ):

            metric = "revenue"
            aggregation = "sum"

        else:

            raise ValueError(
                "Could not determine the business metric."
            )

        # ==================================================
        # 2. DETERMINE GROUPING DIMENSION
        # ==================================================

        group_by = []

        dimension_aliases = {

            "region": [
                "region",
                "regions",
            ],

            "country": [
                "country",
                "countries",
            ],

            "city": [
                "city",
                "cities",
            ],

            "customer_segment": [
                "customer segment",
                "customer segments",
            ],

            "product_category": [
                "product category",
                "product categories",
                "category",
                "categories",
            ],

            "product_subcategory": [
                "product subcategory",
                "product subcategories",
                "subcategory",
                "subcategories",
            ],

            "customer_id": [
                "customer",
                "customers",
                "customer id",
                "customer ids",
            ],

            "product_name": [
                "product name",
                "product names",
            ],
        }

        for dimension, aliases in dimension_aliases.items():

            if any(
                alias in query
                for alias in aliases
            ):

                group_by.append(
                    dimension
                )

        # ==================================================
        # 3. DETERMINE FILTERS
        # ==================================================

        filters = {}

        countries = [
            "India",
            "USA",
            "Canada",
            "Germany",
            "France",
            "Australia",
        ]

        for country in countries:

            if country.lower() in query:

                filters["country"] = country

                break

        # ==================================================
        # 4. DETERMINE TIME RANGE
        # ==================================================

        time_range = None

        months = {

            "january": "01",
            "february": "02",
            "march": "03",
            "april": "04",
            "may": "05",
            "june": "06",
            "july": "07",
            "august": "08",
            "september": "09",
            "october": "10",
            "november": "11",
            "december": "12",
        }

        # Support common abbreviated month names too.

        month_aliases = {

            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "sept": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12",
        }

        for month_name, month_number in months.items():

            if month_name in query:

                time_range = (
                    f"2024-{month_number}"
                )

                break

        if time_range is None:

            for month_name, month_number in month_aliases.items():

                if re.search(
                    rf"\b{month_name}\b",
                    query,
                ):

                    time_range = (
                        f"2024-{month_number}"
                    )

                    break

        # ==================================================
        # 5. DETERMINE RANKING
        # ==================================================

        ranking = None

        top_match = re.search(
            r"\btop\s+(\d+)",
            query,
        )

        bottom_match = re.search(
            r"\bbottom\s+(\d+)",
            query,
        )

        # ==================================================
        # TOP / BOTTOM N
        # ==================================================

        if top_match:

            ranking = {
                "direction": "desc",
                "limit": int(
                    top_match.group(1)
                ),
            }

        elif bottom_match:

            ranking = {
                "direction": "asc",
                "limit": int(
                    bottom_match.group(1)
                ),
            }

        # ==================================================
        # TOP 3 CUSTOMERS PER REGION
        # ==================================================
        #
        # Example:
        #
        # "Revenue of top 3 customers per region"
        #
        # Meaning:
        #
        # For every region:
        #
        #     calculate customer revenue
        #     rank customers by revenue
        #     keep the top 3
        #
        # This requires partitioned ranking.
        #
        # SQL concept:
        #
        # ROW_NUMBER() OVER (
        #     PARTITION BY region
        #     ORDER BY revenue DESC
        # )
        #
        # ==================================================

        if (
            (
                "customer" in query
                or "customers" in query
            )
            and (
                "per region" in query
                or "by region" in query
                or "in each region" in query
                or "for each region" in query
            )
            and top_match
        ):

            ranking = {
                "direction": "desc",
                "limit": int(
                    top_match.group(1)
                ),
                "partition_by": "region",
                "rank_dimension": "customer_id",
            }

            group_by = [
                "region",
                "customer_id",
            ]

        # ==================================================
        # TOP PRODUCT IN EACH REGION
        # ==================================================

        elif (
            "top product in each region" in query
            or "top product for each region" in query
            or "best product in each region" in query
            or "best product for each region" in query
        ):

            ranking = {
                "direction": "desc",
                "limit": 1,
                "partition_by": "region",
                "rank_dimension": "product_name",
            }

            group_by = [
                "region",
                "product_name",
            ]

        # ==================================================
        # 6. DETERMINE COMPARISON
        # ==================================================

        comparison = None

        # ==================================================
        # TARGET COMPARISON
        # ==================================================

        target_keywords = [
            "target",
            "targeted",
            "missed its target",
            "missed target",
        ]

        if any(
            keyword in query
            for keyword in target_keywords
        ):

            comparison = {
                "type": "target",
                "operator": "below",
            }

        # ==================================================
        # CONTRIBUTION PERCENTAGE
        # ==================================================

        elif (
            "contribution" in query
            or "contribution %" in query
            or "contribution percentage" in query
        ):

            comparison = {
                "type": "contribution_percentage"
            }

        # ==================================================
        # YEAR-OVER-YEAR GROWTH
        # ==================================================

        elif (
            "yoy" in query
            or "year over year" in query
            or "year-over-year" in query
            or "year on year" in query
            or "year-on-year" in query
        ):

            comparison = {
                "type": "yoy"
            }

        # ==================================================
        # 7. BUILD QUERY PLAN
        # ==================================================

        return QueryPlan(

            metric=metric,

            aggregation=aggregation,

            group_by=group_by,

            filters=filters,

            time_range=time_range,

            ranking=ranking,

            comparison=comparison,
        )


# ==================================================
# PUBLIC PARSER FUNCTION
# ==================================================

def parse_natural_language_query(
    user_query: str
) -> QueryPlan:
    """
    Convert natural language into a QueryPlan.

    Currently uses the free MockGenAIProvider.
    """

    if not user_query or not user_query.strip():

        raise ValueError(
            "Query cannot be empty."
        )

    provider = MockGenAIProvider()

    return provider.generate_query_plan(
        user_query
    )