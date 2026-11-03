"""JWT real y sesiones PostgreSQL. No simula la identidad autenticada.

Solo se reemplaza get_db para usar un esquema temporal de cursos_test.
Usuarios, sesiones y tokens se preparan como fixtures: no prueba un login.
"""
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema

from app.auth.models import AccessSession
from app.database import Base, User
from app.dependencies import get_db
from app.main import app


@pytest.fixture(scope="module")
def auth_engine():
    value = os.environ.get("TEST_DATABASE_URL")
    if not value:
        pytest.fail("Definí TEST_DATABASE_URL para cursos_test.", pytrace=False)
    url = make_url(value)
    if url.drivername != "postgresql+psycopg" or url.database != "cursos_test":
        pytest.fail("Solo se admite PostgreSQL con base cursos_test.", pytrace=False)
    engine = create_engine(url, connect_args={"connect_timeout": 5})
    schema = "test_auth_" + uuid4().hex
    scoped = engine.execution_options(schema_translate_map={None: schema})
    try:
        with engine.begin() as connection:
            if connection.scalar(text("SELECT current_database()")) != "cursos_test":
                pytest.fail("Base de testing incorrecta.", pytrace=False)
            connection.execute(CreateSchema(schema))
        try:
            Base.metadata.create_all(scoped)
            yield scoped
        finally:
            with engine.begin() as connection:
                connection.execute(DropSchema(schema, cascade=True))
    finally:
        engine.dispose()


@pytest.fixture
def auth_db(auth_engine):
    with auth_engine.connect() as connection:
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def auth_config(monkeypatch):
    config = {
        "JWT_SIGNING_KEY": "clave-exclusiva-de-tests-" + "x" * 40,
        "JWT_ISSUER": "cursos-tests", "JWT_AUDIENCE": "cursos-web-tests",
        "COOKIE_SECURE": "false",
    }
    for name, value in config.items():
        monkeypatch.setenv(name, value)
    return config


@pytest.fixture
def client(auth_db, auth_config):
    def override_db():
        yield auth_db

    previous = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.fixture
def identity(auth_db):
    now = datetime.now(timezone.utc)
    user = User(
        email="persona@example.test", display_name="Persona de pruebas",
        password_hash="hash-ficticio-fixture", role="student",
        email_verified_at=now - timedelta(days=1),
    )
    auth_db.add(user)
    auth_db.flush()
    session = AccessSession(
        user_id=user.id, created_at=now - timedelta(seconds=1),
        expires_at=now + timedelta(minutes=15),
    )
    auth_db.add(session)
    auth_db.flush()
    return user, session


@pytest.fixture
def claims(identity, auth_config):
    user, session = identity
    now = int(datetime.now(timezone.utc).timestamp())
    return {
        "sub": str(user.id), "jti": str(session.id),
        "iss": auth_config["JWT_ISSUER"], "aud": auth_config["JWT_AUDIENCE"],
        "iat": now, "nbf": now, "exp": now + 900,
    }


def set_token(client, claims, config, *, algorithm="HS256", key=None):
    token = jwt.encode(claims, key or config["JWT_SIGNING_KEY"], algorithm=algorithm)
    client.cookies.set("access_token_dev", token)


def test_me_valid_token_returns_current_identity_without_hash(client, claims, identity, auth_config):
    # Arrange
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == str(identity[0].id)
    assert "password_hash" not in response.json()


def test_me_without_cookie_returns_401(client):
    # Arrange
    client.cookies.clear()
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_unparseable_token_returns_401(client):
    # Arrange
    client.cookies.set("access_token_dev", "token-alterado")
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


@pytest.mark.parametrize("field", ["sub", "jti", "iss", "aud", "iat", "nbf", "exp"])
def test_me_missing_required_claim_returns_401(client, claims, auth_config, field):
    # Arrange
    claims.pop(field)
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


@pytest.mark.parametrize("field", ["iss", "aud"])
def test_me_wrong_issuer_or_audience_returns_401(client, claims, auth_config, field):
    # Arrange
    claims[field] = "otro-servicio"
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_wrong_signature_returns_401(client, claims, auth_config):
    # Arrange
    set_token(client, claims, auth_config, key="otra-clave-de-tests-" + "y" * 40)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_unapproved_algorithm_returns_401(client, claims, auth_config):
    # Arrange
    set_token(client, claims, auth_config, algorithm="HS384")
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_expired_jwt_returns_401(client, claims, auth_config):
    # Arrange
    now = int(datetime.now(timezone.utc).timestamp())
    claims.update(iat=now - 1200, nbf=now - 1200, exp=now - 300)
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_future_token_returns_401(client, claims, auth_config):
    # Arrange
    now = int(datetime.now(timezone.utc).timestamp())
    claims.update(iat=now + 120, nbf=now + 120, exp=now + 1020)
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


@pytest.mark.parametrize("field", ["sub", "jti"])
def test_me_malformed_uuid_returns_401(client, claims, auth_config, field):
    # Arrange
    claims[field] = "identificador-invalido"
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


@pytest.mark.parametrize("field", ["iat", "nbf", "exp"])
def test_me_non_integer_timestamp_returns_401(client, claims, auth_config, field):
    # Arrange
    claims[field] = str(claims[field])
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_excessive_lifetime_returns_401(client, claims, auth_config):
    # Arrange
    claims["exp"] = claims["iat"] + 3600
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_revoked_session_returns_401(client, claims, identity, auth_db, auth_config):
    # Arrange
    identity[1].revoked_at = datetime.now(timezone.utc)
    auth_db.flush()
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_expired_database_session_returns_401(client, claims, identity, auth_db, auth_config):
    # Arrange
    now = datetime.now(timezone.utc)
    identity[1].created_at = now - timedelta(minutes=20)
    identity[1].expires_at = now - timedelta(minutes=5)
    auth_db.flush()
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_unknown_session_returns_401(client, claims, auth_config):
    # Arrange
    claims["jti"] = str(uuid4())
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_session_of_another_user_returns_401(client, claims, auth_config):
    # Arrange
    claims["sub"] = str(uuid4())
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_inactive_user_returns_401(client, claims, identity, auth_db, auth_config):
    # Arrange
    identity[0].is_active = False
    auth_db.flush()
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 401


def test_me_unverified_email_returns_403(client, claims, identity, auth_db, auth_config):
    # Arrange
    identity[0].email_verified_at = None
    auth_db.flush()
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert (response.status_code, response.json()["detail"]["code"]) == (403, "EMAIL_NOT_VERIFIED")


def test_me_role_comes_from_database_not_jwt(client, claims, auth_config):
    # Arrange
    claims["role"] = "admin"
    set_token(client, claims, auth_config)
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert (response.status_code, response.json()["role"]) == (200, "student")


def test_me_missing_secret_returns_503(client, claims, auth_config, monkeypatch):
    # Arrange
    set_token(client, claims, auth_config)
    monkeypatch.delenv("JWT_SIGNING_KEY")
    # Act
    response = client.get("/api/v1/auth/me")
    # Assert
    assert response.status_code == 503
