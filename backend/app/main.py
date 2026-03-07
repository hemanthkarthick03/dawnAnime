from fastapi import FastAPI
from sqlalchemy import text
from db.engine import engine
from app.api.health import router as health_router

API_PREFIX = "/api/v1"


app = FastAPI(
    title = "DawnAnime Studio API",
    description = "API for DawnAnime Studio",
    version = "1.0.0",
    docs_url=f"{API_PREFIX}/docs"
)


app.include_router(health_router, prefix=API_PREFIX, tags=["Health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)