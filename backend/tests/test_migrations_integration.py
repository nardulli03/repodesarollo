"""Upgrade, repetición y reversión en esquemas temporales de cursos_test.

Nunca usa DATABASE_URL ni ejecuta downgrade sobre la base de desarrollo.
"""
import os
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.schema import CreateSchema

from app.database import Base, Category


@pytest.fixture
def migration_environment():
    value = os.environ.get("TEST_DATABASE_URL")
    if not value:
        pytest.fail("Definí TEST_DATABASE_URL para cursos_test.", pytrace=False)
    url = make_url(value)
    if url.drivername != "postgresql+psycopg" or url.database != "cursos_test":
        pytest.fail("Estas pruebas solo admiten PostgreSQL con base cursos_test.", pytrace=False)
    engine = create_engine(url, connect_args={"connect_timeout": 5}, hide_parameters=True)
    schema = "test_migration_" + uuid4().hex
    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                if connection.scalar(text("SELECT current_database()")) != "cursos_test":
                    pytest.fail("Base de testing incorrecta.", pytrace=False)
                connection.execute(CreateSchema(schema))
                # El nombre es interno y contiene solamente prefijo fijo y UUID hex.
                connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
                config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
                config.attributes["connection"] = connection
                config.attributes["version_table_schema"] = schema
                yield config, connection, schema
            finally:
                transaction.rollback()
    finally:
        engine.dispose()


def test_initial_upgrade_creates_models_and_repeat_preserves_data(migration_environment):
    # Arrange
    config, connection, schema = migration_environment
    # Act
    command.upgrade(config, "head")
    category_id = uuid4()
    connection.execute(Category.__table__.insert().values(id=category_id, name="Categoría de prueba"))
    command.upgrade(config, "head")
    # Assert
    inspector = inspect(connection)
    assert set(inspector.get_table_names(schema=schema)) == set(Base.metadata.tables) | {"alembic_version"}
    for table in Base.metadata.sorted_tables:
        assert {column["name"] for column in inspector.get_columns(table.name, schema=schema)} == set(table.columns.keys())
    assert connection.scalar(select(Category.id)) == category_id
    version = connection.scalar(text(f'SELECT version_num FROM "{schema}".alembic_version'))
    assert version == "0001_initial"


def test_initial_migration_downgrade_and_reupgrade_in_temporary_schema(migration_environment):
    # Arrange
    config, connection, schema = migration_environment
    command.upgrade(config, "head")
    # Act
    command.downgrade(config, "base")
    after_downgrade = inspect(connection).get_table_names(schema=schema)
    command.upgrade(config, "head")
    # Assert
    assert after_downgrade == ["alembic_version"]
    assert set(inspect(connection).get_table_names(schema=schema)) == set(Base.metadata.tables) | {"alembic_version"}
