from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.query_engine import (
    process_natural_language_query,
)


# ==================================================
# ROUTER
# ==================================================

router = APIRouter(
    prefix="/api",
    tags=["Analytics"],
)


# ==================================================
# REQUEST MODEL
# ==================================================

class QueryRequest(BaseModel):
    query: str


# ==================================================
# HEALTH CHECK
# ==================================================

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Intelligent Analytics Query Engine",
    }


# ==================================================
# NATURAL LANGUAGE QUERY
# ==================================================

@router.post("/query")
def analytics_query(request: QueryRequest):

    try:

        result = process_natural_language_query(
            request.query
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )