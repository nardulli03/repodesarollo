"""Integración real con PostgreSQL exclusivo de testing.

Nunca usa DATABASE_URL. Un esquema aleatorio por ejecución y rollback por test
mantienen aisladas las tablas y los datos. No contiene mocks de persistencia.
"""
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema

from app.database import Base, Category, User
from app.cursos.models import Course
from app.cursos.repository import CursoRepository


@pytest.fixture(scope="module")
def db_engine():
    value = os.environ.get("TEST_DATABASE_URL")
    if not value:
        pytest.fail("Definí TEST_DATABASE_URL para PostgreSQL cursos_test.", pytrace=False)
    url = make_url(value)
    if url.drivername != "postgresql+psycopg" or url.database != "cursos_test":
        pytest.fail("Las pruebas solo admiten postgresql+psycopg y base cursos_test.", pytrace=False)
    engine = create_engine(url, connect_args={"connect_timeout": 5})
    schema = "test_cursos_" + uuid4().hex
    scoped = engine.execution_options(schema_translate_map={None: schema})
    try:
        with engine.begin() as connection:
            if connection.scalar(text("SELECT current_database()")) != "cursos_test":
                pytest.fail("La conexión no corresponde a cursos_test.", pytrace=False)
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
def db_session(db_engine):
    with db_engine.connect() as connection:
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def repo(db_session):
    return CursoRepository(db_session)


@pytest.fixture
def references(db_session):
    author = User(
        email="autor@example.test", display_name="Autor de pruebas",
        password_hash="hash-ficticio-solo-fixture", role="student",
    )
    programming = Category(name="Programación")
    design = Category(name="Diseño")
    db_session.add_all([author, programming, design])
    db_session.flush()
    return {"author": author.id, "programming": programming.id, "design": design.id}


@pytest.fixture
def course_data(references):
    return {
        "created_by": references["author"],
        "category_id": references["programming"],
        "title": "Introducción a Python",
        "topic": "Programación", "provider": "Proveedor educativo",
        "summary": "Curso gratuito para aprender los fundamentos de Python.",
        "description": "Aprendé los fundamentos de Python con explicaciones y ejercicios para principiantes.",
        "url": "https://example.test/python",
        "normalized_url": "https://example.test/python",
        "course_version": "1", "edition_year": 2026,
        "instructors": ["Docente de ejemplo"],
        "has_quizzes": False, "requires_exam": False,
        "grants_certificate": False, "endorsed_by_organization": False,
        "organization_name": None, "author_has_taken": False,
        "language": "es", "level": "inicial", "estimated_minutes": 120,
        "free_content_confirmed": True, "certificate_note": None,
        "status": "published",
    }


@pytest.fixture
def catalog(db_session, course_data, references):
    result = []
    titles = ["Python inicial", "Diseño visual", "Python avanzado", "Redes básicas", "Python para datos"]
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for index, title in enumerate(titles):
        data = {**course_data, "title": title, "created_at": start + timedelta(seconds=index)}
        data.update(url=f"https://example.test/{index}", normalized_url=f"https://example.test/{index}")
        data["category_id"] = references["design"] if index == 1 else references["programming"]
        item = Course(**data)
        db_session.add(item)
        result.append(item)
    for status in ("draft", "in_review", "rejected", "archived"):
        db_session.add(Course(
            created_by=references["author"], title="Python oculto " + status,
            status=status,
        ))
    db_session.flush()
    return result


def test_create_complete_course_get_by_id_roundtrip(repo, db_session, course_data):
    # Arrange
    expected = dict(course_data)
    # Act
    created = repo.create(**course_data)
    course_id = created.id
    db_session.expunge_all()
    recovered = repo.get_by_id(course_id)
    # Assert
    assert {key: getattr(recovered, key) for key in expected} == expected


def test_create_minimal_draft_assigns_defaults(repo, references):
    # Arrange
    data = {"title": "Curso borrador", "created_by": references["author"]}
    # Act
    created = repo.create(**data)
    # Assert
    assert (created.status, created.version, created.instructors) == ("draft", 1, [])


def test_get_by_id_missing_returns_none(repo):
    # Arrange
    missing = uuid4()
    # Act
    result = repo.get_by_id(missing)
    # Assert
    assert result is None


def test_list_empty_returns_envelope(repo):
    # Arrange
    expected = {"items": [], "total": 0, "page": 1, "page_size": 20}
    # Act
    result = repo.list()
    # Assert
    assert result == expected


@pytest.mark.parametrize("page,indices", [(1, [0, 1]), (2, [2, 3]), (3, [4]), (4, [])])
def test_list_page_returns_expected_items_and_real_total(repo, catalog, page, indices):
    # Arrange
    expected = [catalog[index].id for index in indices]
    # Act
    result = repo.list(page=page, page_size=2)
    # Assert
    assert ([item.id for item in result["items"]], result["total"], result["page"], result["page_size"]) == (expected, 5, page, 2)


@pytest.mark.parametrize("query", ["python", "PYTHON", "PyThOn", "  python  "])
def test_list_partial_case_insensitive_search_returns_matches(repo, catalog, query):
    # Arrange
    expected = [catalog[index].id for index in (0, 2, 4)]
    # Act
    result = repo.list(q=query)
    # Assert
    assert ([item.id for item in result["items"]], result["total"]) == (expected, 3)


@pytest.mark.parametrize("field", ["topic", "provider"])
def test_list_search_matches_topic_and_provider(repo, db_session, catalog, field):
    # Arrange
    setattr(catalog[0], field, "PalabraDistintiva")
    db_session.flush()
    # Act
    result = repo.list(q="distintiva")
    # Assert
    assert [item.id for item in result["items"]] == [catalog[0].id]


def test_list_category_returns_only_matching_published_courses(repo, catalog, references):
    # Arrange
    category_id = references["design"]
    # Act
    result = repo.list(category_id=category_id)
    # Assert
    assert ([item.id for item in result["items"]], result["total"]) == ([catalog[1].id], 1)


def test_list_combined_filters_apply_before_pagination(repo, catalog, references):
    # Arrange
    category_id = references["programming"]
    # Act
    result = repo.list(q="python", category_id=category_id, page=2, page_size=2)
    # Assert
    assert ([item.id for item in result["items"]], result["total"]) == ([catalog[4].id], 3)


@pytest.mark.parametrize("query", ["%", "_", "' OR 1=1 --", "sin-coincidencias"])
def test_list_search_treats_user_input_as_literal(repo, catalog, query):
    # Arrange
    expected = ([], 0)
    # Act
    result = repo.list(q=query)
    # Assert
    assert (result["items"], result["total"]) == expected


def test_list_unknown_category_returns_empty(repo, catalog):
    # Arrange
    missing = uuid4()
    # Act
    result = repo.list(category_id=missing)
    # Assert
    assert (result["items"], result["total"]) == ([], 0)


def test_update_partial_preserves_other_fields_and_increments_version(repo, db_session, catalog):
    # Arrange
    course_id = catalog[0].id
    original = (catalog[0].provider, catalog[0].created_by, catalog[0].version)
    # Act
    repo.update(course_id, {"title": "Nuevo título"})
    db_session.expunge_all()
    updated = repo.get_by_id(course_id)
    # Assert
    assert (updated.title, updated.provider, updated.created_by, updated.version) == ("Nuevo título", original[0], original[1], original[2] + 1)


def test_update_missing_returns_none(repo):
    # Arrange
    missing = uuid4()
    # Act
    result = repo.update(missing, {"title": "Nuevo título"})
    # Assert
    assert result is None


@pytest.mark.parametrize("field", ["id", "created_by", "created_at", "version", "unknown"])
def test_update_protected_or_unknown_field_rejects(repo, catalog, field):
    # Arrange
    changes = {field: "valor-no-permitido"}
    # Act
    with pytest.raises(ValueError) as error:
        repo.update(catalog[0].id, changes)
    # Assert
    assert str(error.value) == "COURSE_UPDATE_FIELD_NOT_ALLOWED"


def test_delete_archives_row_and_get_by_id_returns_none(repo, db_session, catalog):
    # Arrange
    course_id = catalog[0].id
    # Act
    result = repo.delete(course_id)
    hidden = repo.get_by_id(course_id)
    stored = db_session.scalar(select(Course).where(Course.id == course_id))
    # Assert
    assert (result, hidden, stored.status) == (True, None, "archived")


def test_delete_removes_course_from_catalog_total(repo, catalog):
    # Arrange
    course_id = catalog[0].id
    # Act
    repo.delete(course_id)
    result = repo.list()
    # Assert
    assert ([item.id for item in result["items"]], result["total"]) == ([item.id for item in catalog[1:]], 4)


def test_delete_missing_returns_false(repo):
    # Arrange
    missing = uuid4()
    # Act
    result = repo.delete(missing)
    # Assert
    assert result is False


def test_create_duplicate_normalized_url_rejects_in_database(repo, db_session, course_data):
    # Arrange
    db_session.add(Course(**course_data))
    db_session.flush()
    # Act
    with pytest.raises(IntegrityError):
        repo.create(**course_data)
    # Assert
    db_session.rollback()


def test_create_unknown_author_rejects_in_database(repo, course_data, db_session):
    # Arrange
    course_data["created_by"] = uuid4()
    # Act
    with pytest.raises(IntegrityError):
        repo.create(**course_data)
    # Assert
    db_session.rollback()
