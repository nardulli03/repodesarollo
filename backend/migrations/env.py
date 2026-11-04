"""Configuración Alembic para PostgreSQL y conexiones aisladas de pruebas."""
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from app.database import Base
# Registrar todos los modelos implementados antes de comparar metadatos.
from app.cursos.models import Course  # noqa: F401
from app.auth.models import AccessSession  # noqa: F401
from app.aportes.models import CourseReview  # noqa: F401


config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name, disable_existing_loggers=False)
target_metadata = Base.metadata


def database_url():
    value = os.environ.get("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL no está configurada para Alembic.")
    url = make_url(value)
    if url.drivername != "postgresql+psycopg":
        raise RuntimeError("Alembic requiere una URL postgresql+psycopg.")
    return url


def run_offline():
    context.configure(
        url=database_url(), target_metadata=target_metadata,
        literal_binds=True, dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def migrate_connection(connection):
    context.configure(
        connection=connection, target_metadata=target_metadata,
        compare_type=True,
        version_table_schema=config.attributes.get("version_table_schema"),
    )
    with context.begin_transaction():
        context.run_migrations()


def run_online():
    supplied = config.attributes.get("connection")
    if supplied is not None:
        migrate_connection(supplied)
        return
    engine = create_engine(database_url(), poolclass=NullPool, hide_parameters=True)
    try:
        with engine.connect() as connection:
            migrate_connection(connection)
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_offline()
else:
    run_online()

