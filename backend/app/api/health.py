from fastapi import APIRouter
from sqlalchemy import text
from db.engine import engine
from app.utils.settings import settings
from db.config import DATABASE_URL

router = APIRouter()

# Health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "API is working!"}

@router.get("/db-health")
async def db_health():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        return {"status" : "PostgreSQL Database connected!",
                "database_url": settings.DATABASE_URL,
                "database_user": settings.DB_USER}
    