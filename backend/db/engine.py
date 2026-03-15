from sqlalchemy.ext.asyncio import create_async_engine
from app.utils.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=10,          # concurrent connections per worker
    max_overflow=20,       # burst connections allowed
    pool_pre_ping=True,    # drops stale connections automatically
    pool_recycle=3600,     # recycle connections every 1hr
)