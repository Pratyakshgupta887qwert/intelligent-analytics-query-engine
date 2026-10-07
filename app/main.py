from fastapi import FastAPI
from app.api.routes import router


app = FastAPI(
    title="Intelligent Analytics Query Engine",
    description=(
        "A GenAI-powered natural language analytics "
        "query engine."
    ),
    version="1.0.0",
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Intelligent Analytics Query Engine is running.",
        "docs": "/docs",
        "health": "/api/health",
    }