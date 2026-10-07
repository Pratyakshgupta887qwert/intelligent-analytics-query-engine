from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryPlan(BaseModel):
    """
    Structured representation of a user's analytical query.

    The GenAI layer produces this plan.
    The deterministic SQL layer converts the plan
    into executable DuckDB SQL.
    """

    metric: str = Field(
        ...,
        description="Business metric such as revenue, profit, orders, or avg_order_value."
    )

    aggregation: str = Field(
        ...,
        description="Aggregation such as sum, count, or average."
    )

    group_by: List[str] = Field(
        default_factory=list,
        description="Dimensions used for grouping."
    )

    filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Filters applied to the dataset."
    )

    time_range: Optional[str] = Field(
        default=None,
        description="Time period mentioned in the query."
    )

    ranking: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Ranking information such as top N or bottom N."
    )

    comparison: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Comparison such as target, YoY, or contribution percentage."
    )