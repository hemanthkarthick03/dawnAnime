from fastapi import APIRouter
from sqlalchemy import text
from db.engine import engine
from app.utils.settings import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    db_connected = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_connected = True
    except Exception:
        db_connected = False
    
    return {
        "status": "ok",
        "db_connected": db_connected,
        "version": "1.0.0"
    }