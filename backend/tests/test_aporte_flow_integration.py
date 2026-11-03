"""Flujo HTTP de aportes con JWT firmado y PostgreSQL real.

Reutiliza únicamente el aislamiento y la conexión de las pruebas de sesiones.
No reemplaza get_current_user ni los controles de permisos/CSRF.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
import pytest

from app.auth.models import AccessSession
from app.cursos.models import Course
from app.database import Category, User
from test_auth_session_integration import auth_config, auth_db, auth_engine, client


@pytest.fixture(autouse=True)
def csrf_config(monkeypatch):
    key = "csrf-key-exclusiva-de-tests-" + "c" * 40
    monkeypatch.setenv("CSRF_SIGNING_KEY", key)
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://testserver")
    return key


@pytest.fixture
def actors(auth_db):
    now = datetime.now(timezone.utc)
    result = {}
    for name, role in (("author", "student"), ("other", "student"), ("admin", "admin")):
        user = User(
            email=f"{name}@example.test", display_name=f"Persona {name}",
            password_hash="hash-ficticio-fixture", role=role,
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
        result[name] = (user, session)
    return result


@pytest.fixture
def payload(auth_db):
    category = Category(name="Programación de pruebas")
    auth_db.add(category)
    auth_db.flush()
    return {
        "category_id": str(category.id), "title": "Introducción a Python",
        "topic": "Programación", "provider": "Proveedor educativo",
        "summary": "Curso gratuito para aprender los fundamentos de Python.",
        "description": "Aprendé los fundamentos de Python con explicaciones y ejercicios para principiantes.",
        "url": "https://example.test/python", "course_version": "1",
        "edition_year": 2026, "instructors": ["Docente de ejemplo"],
        "has_quizzes": False, "requires_exam": False, "grants_certificate": False,
        "endorsed_by_organization": False, "organization_name": None,
        "author_has_taken": False, "language": "es", "level": "inicial",
        "estimated_minutes": 120, "free_content_confirmed": True,
        "certificate_note": None,
    }


def authenticate(client, actor, config):
    user, session = actor
    now = int(datetime.now(timezone.utc).timestamp())
    token = jwt.encode({
        "sub": str(user.id), "jti": str(session.id),
        "iss": config["JWT_ISSUER"], "aud": config["JWT_AUDIENCE"],
        "iat": now, "nbf": now, "exp": now + 900,
    }, config["JWT_SIGNING_KEY"], algorithm="HS256")
    client.cookies.set("access_token_dev", token)


def post(client, path, body, key, *, csrf=True, origin="http://testserver", expired=False):
    headers = {}
    if origin is not None:
        headers["Origin"] = origin
    if csrf:
        now = int(datetime.now(timezone.utc).timestamp())
        token = jwt.encode({
            "purpose": "csrf", "nonce": str(uuid4()),
            "iat": now - 120 if expired else now,
            "exp": now - 60 if expired else now + 43200,
        }, key, algorithm="HS256")
        client.cookies.set("csrf_token_dev", token)
        headers["X-CSRF-Token"] = token
    return client.post(path, json=body, headers=headers)


def draft(client, actors, config, payload, csrf_key):
    authenticate(client, actors["author"], config)
    response = post(client, "/api/v1/me/courses", payload, csrf_key)
    assert response.status_code == 201, response.text
    return response.json()


def pending(client, actors, config, payload, csrf_key):
    created = draft(client, actors, config, payload, csrf_key)
    response = post(client, f"/api/v1/me/courses/{created['id']}/submit", {
        "expected_version": created["version"],
    }, csrf_key)
    assert response.status_code == 200, response.text
    return response.json()


def decide(client, course, key, *, approved=True, reason=None, url_checked=True, version=None):
    return post(client, f"/api/v1/admin/reviews/{course['id']}/decision", {
        "expected_version": course["version"] if version is None else version,
        "approved": approved, "reason": reason, "url_checked": url_checked,
    }, key)


def test_contribution_submit_valid_data_returns_in_review(client, actors, auth_config, payload, csrf_config):
    # Arrange
    created = draft(client, actors, auth_config, payload, csrf_config)
    # Act
    response = post(client, f"/api/v1/me/courses/{created['id']}/submit", {
        "expected_version": created["version"],
    }, csrf_config)
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "in_review"
    assert response.json()["version"] == created["version"] + 1


def test_review_approval_publishes_course_and_excludes_private_fields(client, actors, auth_config, payload, csrf_config):
    # Arrange
    course = pending(client, actors, auth_config, payload, csrf_config)
    authenticate(client, actors["admin"], auth_config)
    # Act
    decision = decide(client, course, csrf_config)
    catalog = client.get("/api/v1/courses")
    # Assert
    assert decision.status_code == 200
    assert decision.json()["status"] == "published"
    assert catalog.status_code == 200
    assert [item["id"] for item in catalog.json()["items"]] == [course["id"]]
    assert "created_by" not in catalog.json()["items"][0]
    assert "author_has_taken" not in catalog.json()["items"][0]


def test_review_rejection_keeps_course_out_of_public_catalog(client, actors, auth_config, payload, csrf_config):
    # Arrange
    course = pending(client, actors, auth_config, payload, csrf_config)
    authenticate(client, actors["admin"], auth_config)
    # Act
    decision = decide(client, course, csrf_config, approved=False,
                      reason="El enlace no permite acceder al contenido.", url_checked=False)
    catalog = client.get("/api/v1/courses")
    # Assert
    assert (decision.status_code, decision.json()["status"]) == (200, "rejected")
    assert (catalog.json()["items"], catalog.json()["total"]) == ([], 0)


def test_contribution_author_without_session_returns_401(client, payload, csrf_config):
    # Arrange
    client.cookies.clear()
    # Act
    response = post(client, "/api/v1/me/courses", payload, csrf_config)
    # Assert
    assert response.status_code == 401


def test_review_student_without_admin_role_returns_403(client, actors, auth_config, payload, csrf_config):
    # Arrange
    course = pending(client, actors, auth_config, payload, csrf_config)
    authenticate(client, actors["other"], auth_config)
    # Act
    response = decide(client, course, csrf_config)
    # Assert
    assert response.status_code == 403


def test_review_admin_own_contribution_returns_403(client, actors, auth_config, payload, csrf_config):
    # Arrange
    admin_as_author = {**actors, "author": actors["admin"]}
    course = pending(client, admin_as_author, auth_config, payload, csrf_config)
    authenticate(client, actors["admin"], auth_config)
    # Act
    response = decide(client, course, csrf_config)
    # Assert
    assert response.status_code == 403


@pytest.mark.parametrize("status", ["draft", "published", "rejected", "archived"])
def test_review_course_not_in_review_returns_409(client, actors, auth_config, payload, csrf_config, auth_db, status):
    # Arrange
    course = pending(client, actors, auth_config, payload, csrf_config)
    auth_db.get(Course, UUID(course["id"])).status = status
    auth_db.flush()
    authenticate(client, actors["admin"], auth_config)
    # Act
    response = decide(client, course, csrf_config)
    # Assert
    assert response.status_code == 409


@pytest.mark.parametrize("reason", [None, "", "corto"])
def test_review_rejection_without_valid_reason_returns_422(client, actors, auth_config, payload, csrf_config, reason):
    # Arrange
    course = pending(client, actors, auth_config, payload, csrf_config)
    authenticate(client, actors["admin"], auth_config)
    # Act
    response = decide(client, course, csrf_config, approved=False, reason=reason)
    # Assert
    assert response.status_code == 422


@pytest.mark.parametrize("checked", [False, None])
def test_review_approval_without_link_confirmation_returns_422(client, actors, auth_config, payload, csrf_config, checked):
    # Arrange
    course = pending(client, actors, auth_config, payload, csrf_config)
    authenticate(client, actors["admin"], auth_config)
    # Act
    response = decide(client, course, csrf_config, url_checked=checked)
    # Assert
    assert response.status_code == 422


def test_review_stale_version_returns_409(client, actors, auth_config, payload, csrf_config):
    # Arrange
    course = pending(client, actors, auth_config, payload, csrf_config)
    authenticate(client, actors["admin"], auth_config)
    # Act
    response = decide(client, course, csrf_config, version=course["version"] - 1)
    # Assert
    assert response.status_code == 409


def test_submit_other_authors_course_returns_404(client, actors, auth_config, payload, csrf_config):
    # Arrange
    course = draft(client, actors, auth_config, payload, csrf_config)
    authenticate(client, actors["other"], auth_config)
    # Act
    response = post(client, f"/api/v1/me/courses/{course['id']}/submit", {
        "expected_version": course["version"],
    }, csrf_config)
    # Assert
    assert response.status_code == 404


def test_submit_revalidates_future_year_and_preserves_draft(client, actors, auth_config, payload, csrf_config, auth_db):
    # Arrange
    course = draft(client, actors, auth_config, payload, csrf_config)
    row = auth_db.get(Course, UUID(course["id"]))
    row.edition_year = datetime.now(timezone.utc).year + 1
    auth_db.flush()
    # Act
    response = post(client, f"/api/v1/me/courses/{course['id']}/submit", {
        "expected_version": course["version"],
    }, csrf_config)
    # Assert
    assert response.status_code == 422
    auth_db.refresh(row)
    assert row.status == "draft"


def test_contribution_duplicate_url_returns_409(client, actors, auth_config, payload, csrf_config):
    # Arrange
    draft(client, actors, auth_config, payload, csrf_config)
    # Act
    response = post(client, "/api/v1/me/courses", payload, csrf_config)
    # Assert
    assert response.status_code == 409


def test_contribution_cannot_choose_owner_or_status(client, actors, auth_config, payload, csrf_config):
    # Arrange
    authenticate(client, actors["author"], auth_config)
    payload.update(created_by=str(actors["admin"][0].id), status="published")
    # Act
    response = post(client, "/api/v1/me/courses", payload, csrf_config)
    # Assert
    assert response.status_code == 422


def test_contribution_missing_csrf_returns_403(client, actors, auth_config, payload, csrf_config):
    # Arrange
    authenticate(client, actors["author"], auth_config)
    # Act
    response = post(client, "/api/v1/me/courses", payload, csrf_config, csrf=False)
    # Assert
    assert response.status_code == 403


def test_contribution_wrong_origin_returns_403(client, actors, auth_config, payload, csrf_config):
    # Arrange
    authenticate(client, actors["author"], auth_config)
    # Act
    response = post(client, "/api/v1/me/courses", payload, csrf_config, origin="https://otro.example")
    # Assert
    assert response.status_code == 403


def test_contribution_wrong_csrf_signature_returns_403(client, actors, auth_config, payload, csrf_config):
    # Arrange
    authenticate(client, actors["author"], auth_config)
    # Act
    response = post(client, "/api/v1/me/courses", payload, "clave-incorrecta-" + "z" * 40)
    # Assert
    assert response.status_code == 403


def test_contribution_expired_csrf_returns_403(client, actors, auth_config, payload, csrf_config):
    # Arrange
    authenticate(client, actors["author"], auth_config)
    # Act
    response = post(client, "/api/v1/me/courses", payload, csrf_config, expired=True)
    # Assert
    assert response.status_code == 403


def test_csrf_endpoint_issues_token_and_cookie(client):
    # Arrange
    client.cookies.clear()
    # Act
    response = client.get("/api/v1/auth/csrf")
    # Assert
    assert response.status_code == 200
    assert response.json()["csrf_token"] == client.cookies.get("csrf_token_dev")


def test_catalog_query_filters_persisted_approved_courses(client, actors, auth_config, payload, csrf_config):
    # Arrange
    first = pending(client, actors, auth_config, payload, csrf_config)
    authenticate(client, actors["admin"], auth_config)
    assert decide(client, first, csrf_config).status_code == 200
    second_payload = {**payload, "title": "Curso de redes", "url": "https://example.test/redes"}
    second = pending(client, actors, auth_config, second_payload, csrf_config)
    authenticate(client, actors["admin"], auth_config)
    assert decide(client, second, csrf_config).status_code == 200
    client.cookies.clear()
    # Act
    response = client.get("/api/v1/courses", params={
        "q": "PYTHON", "category_id": payload["category_id"], "page_size": 1,
    })
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert ([item["id"] for item in data["items"]], data["total"], data["page_size"]) == ([first["id"]], 1, 1)

