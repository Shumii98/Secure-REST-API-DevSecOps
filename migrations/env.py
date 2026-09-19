import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

import src.models  # noqa: F401 — registers all models on Base.metadata
from src.database import Base

# Make `src` importable when running `alembic` from the project root.
sys.path.insert(0, os.getcwd())

# Load DATABASE_URL and other settings from .env
load_dotenv()

config = context.config

# SQLite by default for local dev — matches src/database.py.
# Override via .env's DATABASE_URL when you move to Postgres.
db_url = os.environ.get("DATABASE_URL", "sqlite:///./secure_api_dev.db")
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()