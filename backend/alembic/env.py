import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.engine import Connection

from alembic import context
from dotenv import load_dotenv

from app.db.base import Base

# ── Load .env before anything else ──────────────────────────────────────────
load_dotenv()

config = context.config

# ── Logging ──────────────────────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Inject DB URL from environment (overrides alembic.ini) ───────────────────
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    # asyncpg driver required for async migrations
    config.set_main_option(
        "sqlalchemy.url",
        DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    )

# ── Import all models to register them with Base.metadata ───────────────────
import app.db.models  # This triggers model registration

target_metadata = Base.metadata

# ── Optional: multi-tenant schema support ────────────────────────────────────
SCHEMA = os.environ.get("DB_SCHEMA", "public")


# ── Offline mode ─────────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Useful for generating SQL scripts without a live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=SCHEMA,   # ✅ schema-aware versioning
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode ───────────────────────────────────────────────────────────────
def do_run_migrations(connection: Connection) -> None:    # ✅ typed
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=SCHEMA,                      # ✅ schema-aware
        include_schemas=True,                             # ✅ detect schema changes
        compare_type=True,                                # ✅ detect column type changes
        compare_server_default=True,                      # ✅ detect default value changes
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,    # ✅ NullPool correct for migration scripts
    )

    async with connectable.connect() as connection:
        # ✅ Set search_path for schema-aware migrations
        if SCHEMA != "public":
            await connection.execute(text(f"SET search_path TO {SCHEMA}"))

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()     # ✅ explicit cleanup


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ── Entry point ───────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()