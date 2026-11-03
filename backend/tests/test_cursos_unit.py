import pytest

from app.cursos.rules import (
    transition_course,
    validate_course_contribution,
)


@pytest.fixture
def valid_course():
    return {
        "title": "Introducción a Python",
        "topic": "Programación",
        "provider": "Proveedor educativo",
        "category_id": "programacion",
        "summary": "Curso gratuito de introducción a Python.",
        "description": (
            "Aprendé los fundamentos de Python mediante explicaciones "
            "y ejercicios prácticos para principiantes."
        ),
        "url": "https://example.com/python",
        "course_version": "1",
        "edition_year": 2026,
        "instructors": ["Docente de ejemplo"],
        "has_quizzes": False,
        "requires_exam": False,
        "grants_certificate": False,
        "endorsed_by_organization": False,
        "organization_name": None,
        "author_has_taken": False,
        "language": "es",
        "level": "inicial",
        "estimated_minutes": 120,
        "free_content_confirmed": True,
        "certificate_note": None,
    }


def test_validate_course_contribution_valid_data_accepts(valid_course):
    # Arrange
    current_year = 2026
    existing_urls = set()

    # Act
    result = validate_course_contribution(
        valid_course,
        current_year=current_year,
        existing_urls=existing_urls,
    )

    # Assert
    assert result is None


@pytest.mark.parametrize("title", [None, "", "   "])
def test_validate_course_contribution_missing_title_rejects(
    valid_course, title
):
    # Arrange
    valid_course["title"] = title

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course,
            current_year=2026,
            existing_urls=set(),
        )

    # Assert
    assert str(error.value) == "COURSE_TITLE_REQUIRED"


def test_validate_course_contribution_future_year_rejects(valid_course):
    # Arrange
    valid_course["edition_year"] = 2027

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course,
            current_year=2026,
            existing_urls=set(),
        )

    # Assert
    assert str(error.value) == "COURSE_YEAR_INVALID"


@pytest.mark.parametrize(
    "current_status,new_status",
    [
        ("draft", "in_review"),
        ("in_review", "published"),
        ("in_review", "rejected"),
        ("rejected", "draft"),
    ],
)
def test_transition_course_allowed_transition_returns_new_status(
    current_status, new_status
):
    # Arrange
    expected = new_status

    # Act
    result = transition_course(current_status, new_status)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "current_status,new_status",
    [
        ("draft", "published"),
        ("rejected", "published"),
        ("archived", "draft"),
        ("unknown", "published"),
    ],
)
def test_transition_course_forbidden_transition_rejects(
    current_status, new_status
):
    # Arrange
    expected_code = "COURSE_TRANSITION_NOT_ALLOWED"

    # Act
    with pytest.raises(ValueError) as error:
        transition_course(current_status, new_status)

    # Assert
    assert str(error.value) == expected_code


@pytest.mark.parametrize(
    "url",
    [
        None,
        "",
        "   ",
        "http://example.com/python",
        "https://",
        "javascript:alert(1)",
        "https://user:password@example.com/python",
        "https://example.com:abc/python",
    ],
)
def test_validate_course_contribution_invalid_url_rejects(
    valid_course, url
):
    # Arrange
    valid_course["url"] = url

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course,
            current_year=2026,
            existing_urls=set(),
        )

    # Assert
    assert str(error.value) == "COURSE_URL_INVALID"


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/python",
        "https://EXAMPLE.COM/python#contenido",
        "https://example.com:443/python",
    ],
)
def test_validate_course_contribution_duplicate_url_rejects(
    valid_course, url
):
    # Arrange
    valid_course["url"] = url
    existing_urls = {"https://example.com/python"}

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course,
            current_year=2026,
            existing_urls=existing_urls,
        )

    # Assert
    assert str(error.value) == "COURSE_URL_DUPLICATE"


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/otro-curso",
        "https://example.com/python?edition=2",
    ],
)
def test_validate_course_contribution_different_url_accepts(
    valid_course, url
):
    # Arrange
    valid_course["url"] = url
    existing_urls = {"https://example.com/python"}

    # Act
    result = validate_course_contribution(
        valid_course,
        current_year=2026,
        existing_urls=existing_urls,
    )

    # Assert
    assert result is None


@pytest.mark.parametrize(
    "field",
    [
        "topic",
        "provider",
        "category_id",
        "summary",
        "description",
        "language",
        "level",
    ],
)
@pytest.mark.parametrize("value", [None, "", "   "])
def test_validate_course_contribution_missing_field_rejects(
    valid_course, field, value
):
    # Arrange
    valid_course[field] = value

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course,
            current_year=2026,
            existing_urls=set(),
        )

    # Assert
    assert str(error.value) == f"COURSE_FIELD_REQUIRED:{field}"


@pytest.mark.parametrize(
    "field",
    [
        "has_quizzes",
        "requires_exam",
        "grants_certificate",
        "endorsed_by_organization",
        "author_has_taken",
        "free_content_confirmed",
    ],
)
@pytest.mark.parametrize("value", [None, "false", 0])
def test_validate_course_contribution_invalid_flag_rejects(
    valid_course, field, value
):
    # Arrange
    valid_course[field] = value

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course,
            current_year=2026,
            existing_urls=set(),
        )

    # Assert
    assert str(error.value) == f"COURSE_FLAG_INVALID:{field}"


def test_validate_course_contribution_endorsement_without_name_rejects(
    valid_course,
):
    # Arrange
    valid_course["endorsed_by_organization"] = True
    valid_course["organization_name"] = None

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course,
            current_year=2026,
            existing_urls=set(),
        )

    # Assert
    assert str(error.value) == "COURSE_ORGANIZATION_REQUIRED"


def test_validate_course_contribution_not_free_rejects(valid_course):
    # Arrange
    valid_course["free_content_confirmed"] = False

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course,
            current_year=2026,
            existing_urls=set(),
        )

    # Assert
    assert str(error.value) == "COURSE_NOT_FREE"


# Última tanda: límites y metadatos del aporte.

@pytest.mark.parametrize(
    "field,minimum,maximum",
    [
        ("title", 3, 150),
        ("topic", 2, 100),
        ("provider", 2, 100),
        ("summary", 20, 300),
        ("description", 50, 10000),
    ],
)
@pytest.mark.parametrize("boundary", ["below_minimum", "above_maximum"])
def test_validate_course_contribution_text_outside_limits_rejects(
    valid_course, field, minimum, maximum, boundary
):
    # Arrange
    length = minimum - 1 if boundary == "below_minimum" else maximum + 1
    valid_course[field] = "x" * length

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course, current_year=2026, existing_urls=set()
        )

    # Assert
    assert str(error.value) == f"COURSE_FIELD_LENGTH:{field}"


@pytest.mark.parametrize(
    "field,minimum,maximum",
    [
        ("title", 3, 150),
        ("topic", 2, 100),
        ("provider", 2, 100),
        ("summary", 20, 300),
        ("description", 50, 10000),
    ],
)
@pytest.mark.parametrize("boundary", ["minimum", "maximum"])
def test_validate_course_contribution_text_at_limits_accepts(
    valid_course, field, minimum, maximum, boundary
):
    # Arrange
    length = minimum if boundary == "minimum" else maximum
    valid_course[field] = "x" * length

    # Act
    result = validate_course_contribution(
        valid_course, current_year=2026, existing_urls=set()
    )

    # Assert
    assert result is None


@pytest.mark.parametrize("minutes", [None, 0, -1, 100001, True, "120", 1.5])
def test_validate_course_contribution_invalid_duration_rejects(
    valid_course, minutes
):
    # Arrange
    valid_course["estimated_minutes"] = minutes

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course, current_year=2026, existing_urls=set()
        )

    # Assert
    assert str(error.value) == "COURSE_DURATION_INVALID"


@pytest.mark.parametrize("minutes", [1, 100000])
def test_validate_course_contribution_duration_at_limits_accepts(
    valid_course, minutes
):
    # Arrange
    valid_course["estimated_minutes"] = minutes

    # Act
    result = validate_course_contribution(
        valid_course, current_year=2026, existing_urls=set()
    )

    # Assert
    assert result is None


@pytest.mark.parametrize("year", [1899, True, "2026", 2026.5])
def test_validate_course_contribution_invalid_year_type_or_range_rejects(
    valid_course, year
):
    # Arrange
    valid_course["edition_year"] = year

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course, current_year=2026, existing_urls=set()
        )

    # Assert
    assert str(error.value) == "COURSE_YEAR_INVALID"


@pytest.mark.parametrize("year", [None, 1900, 2026])
def test_validate_course_contribution_allowed_year_accepts(valid_course, year):
    # Arrange
    valid_course["edition_year"] = year

    # Act
    result = validate_course_contribution(
        valid_course, current_year=2026, existing_urls=set()
    )

    # Assert
    assert result is None


@pytest.mark.parametrize(
    "field,value,error_code",
    [
        ("language", "fr", "COURSE_LANGUAGE_INVALID"),
        ("language", "ES", "COURSE_LANGUAGE_INVALID"),
        ("level", "experto", "COURSE_LEVEL_INVALID"),
        ("level", "Inicial", "COURSE_LEVEL_INVALID"),
    ],
)
def test_validate_course_contribution_unknown_option_rejects(
    valid_course, field, value, error_code
):
    # Arrange
    valid_course[field] = value

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course, current_year=2026, existing_urls=set()
        )

    # Assert
    assert str(error.value) == error_code


@pytest.mark.parametrize("language", ["es", "en", "pt"])
def test_validate_course_contribution_supported_language_accepts(
    valid_course, language
):
    # Arrange
    valid_course["language"] = language

    # Act
    result = validate_course_contribution(
        valid_course, current_year=2026, existing_urls=set()
    )

    # Assert
    assert result is None


@pytest.mark.parametrize("level", ["inicial", "intermedio", "avanzado"])
def test_validate_course_contribution_supported_level_accepts(valid_course, level):
    # Arrange
    valid_course["level"] = level

    # Act
    result = validate_course_contribution(
        valid_course, current_year=2026, existing_urls=set()
    )

    # Assert
    assert result is None


@pytest.mark.parametrize("version", [123, "", "x" * 81])
def test_validate_course_contribution_invalid_course_version_rejects(
    valid_course, version
):
    # Arrange
    valid_course["course_version"] = version

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course, current_year=2026, existing_urls=set()
        )

    # Assert
    assert str(error.value) == "COURSE_VERSION_INVALID"


@pytest.mark.parametrize("version", [None, "1", "x" * 80])
def test_validate_course_contribution_optional_version_accepts(
    valid_course, version
):
    # Arrange
    valid_course["course_version"] = version

    # Act
    result = validate_course_contribution(
        valid_course, current_year=2026, existing_urls=set()
    )

    # Assert
    assert result is None


@pytest.mark.parametrize(
    "instructors",
    [None, "Docente", ["A"], ["   "], ["x" * 121], [42], ["Docente"] * 21],
)
def test_validate_course_contribution_invalid_instructors_rejects(
    valid_course, instructors
):
    # Arrange
    valid_course["instructors"] = instructors

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course, current_year=2026, existing_urls=set()
        )

    # Assert
    assert str(error.value) == "COURSE_INSTRUCTORS_INVALID"


@pytest.mark.parametrize("instructors", [[], ["AB"], ["x" * 120] * 20])
def test_validate_course_contribution_allowed_instructors_accepts(
    valid_course, instructors
):
    # Arrange
    valid_course["instructors"] = instructors

    # Act
    result = validate_course_contribution(
        valid_course, current_year=2026, existing_urls=set()
    )

    # Assert
    assert result is None


@pytest.mark.parametrize("name", [None, "", "   ", 42])
def test_validate_course_contribution_missing_endorser_name_rejects(
    valid_course, name
):
    # Arrange
    valid_course["endorsed_by_organization"] = True
    valid_course["organization_name"] = name

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course, current_year=2026, existing_urls=set()
        )

    # Assert
    assert str(error.value) == "COURSE_ORGANIZATION_REQUIRED"


@pytest.mark.parametrize("name", ["A", "x" * 151])
def test_validate_course_contribution_endorser_length_invalid_rejects(
    valid_course, name
):
    # Arrange
    valid_course["endorsed_by_organization"] = True
    valid_course["organization_name"] = name

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course, current_year=2026, existing_urls=set()
        )

    # Assert
    assert str(error.value) == "COURSE_FIELD_LENGTH:organization_name"


@pytest.mark.parametrize("name", ["AB", "x" * 150])
def test_validate_course_contribution_valid_endorsement_accepts(
    valid_course, name
):
    # Arrange
    valid_course["endorsed_by_organization"] = True
    valid_course["organization_name"] = name

    # Act
    result = validate_course_contribution(
        valid_course, current_year=2026, existing_urls=set()
    )

    # Assert
    assert result is None


def test_validate_course_contribution_name_without_endorsement_rejects(valid_course):
    # Arrange
    valid_course["endorsed_by_organization"] = False
    valid_course["organization_name"] = "Organización de ejemplo"

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course, current_year=2026, existing_urls=set()
        )

    # Assert
    assert str(error.value) == "COURSE_ORGANIZATION_UNEXPECTED"


@pytest.mark.parametrize("note", [42, "x" * 501])
def test_validate_course_contribution_invalid_certificate_note_rejects(
    valid_course, note
):
    # Arrange
    valid_course["certificate_note"] = note

    # Act
    with pytest.raises(ValueError) as error:
        validate_course_contribution(
            valid_course, current_year=2026, existing_urls=set()
        )

    # Assert
    assert str(error.value) == "COURSE_CERTIFICATE_NOTE_INVALID"


@pytest.mark.parametrize("note", [None, "", "x" * 500])
def test_validate_course_contribution_allowed_certificate_note_accepts(
    valid_course, note
):
    # Arrange
    valid_course["certificate_note"] = note

    # Act
    result = validate_course_contribution(
        valid_course, current_year=2026, existing_urls=set()
    )

    # Assert
    assert result is None


def test_validate_course_contribution_does_not_modify_input(valid_course):
    # Arrange
    from copy import deepcopy

    original = deepcopy(valid_course)
    existing_urls = {"https://example.com/otro-curso"}
    original_urls = existing_urls.copy()

    # Act
    validate_course_contribution(
        valid_course, current_year=2026, existing_urls=existing_urls
    )

    # Assert
    assert (valid_course, existing_urls) == (original, original_urls)


@pytest.mark.parametrize(
    "current_status,new_status",
    [
        ("draft", "archived"),
        ("in_review", "archived"),
        ("rejected", "archived"),
        ("published", "archived"),
        ("published", "draft"),
    ],
)
def test_transition_course_documented_edit_or_archive_returns_new_status(
    current_status, new_status
):
    # Arrange
    expected = new_status

    # Act
    result = transition_course(current_status, new_status)

    # Assert
    assert result == expected


@pytest.mark.parametrize("new_status", ["in_review", "published", "rejected", "archived"])
def test_transition_course_archived_is_terminal_rejects(new_status):
    # Arrange
    current_status = "archived"

    # Act
    with pytest.raises(ValueError) as error:
        transition_course(current_status, new_status)

    # Assert
    assert str(error.value) == "COURSE_TRANSITION_NOT_ALLOWED"
