from copy import deepcopy

import pytest

from app.aportes.rules import validate_review


@pytest.fixture
def course():
    return {"id": "curso-1", "created_by": "autor-1", "status": "in_review"}


@pytest.fixture
def review():
    return {
        "reviewer_id": "admin-1",
        "reviewer_role": "admin",
        "decision": "approved",
        "reason": None,
        "url_checked": True,
    }


def test_validate_review_admin_approval_returns_published(course, review):
    # Arrange
    expected = "published"
    # Act
    result = validate_review(course, **review)
    # Assert
    assert result == expected


def test_validate_review_admin_rejection_returns_rejected(course, review):
    # Arrange
    review.update(decision="rejected", reason="El enlace no permite acceder.", url_checked=False)
    # Act
    result = validate_review(course, **review)
    # Assert
    assert result == "rejected"


@pytest.mark.parametrize("role", ["student", "guest", None, "ADMIN"])
def test_validate_review_non_admin_rejects(course, review, role):
    # Arrange
    review["reviewer_role"] = role
    # Act
    with pytest.raises(ValueError) as error:
        validate_review(course, **review)
    # Assert
    assert str(error.value) == "REVIEW_ADMIN_REQUIRED"


@pytest.mark.parametrize("decision", ["approved", "rejected"])
def test_validate_review_own_contribution_rejects(course, review, decision):
    # Arrange
    review.update(reviewer_id="autor-1", decision=decision, reason="Motivo suficientemente largo.")
    # Act
    with pytest.raises(ValueError) as error:
        validate_review(course, **review)
    # Assert
    assert str(error.value) == "REVIEW_SELF_REVIEW_FORBIDDEN"


@pytest.mark.parametrize("status", ["draft", "published", "rejected", "archived", "unknown"])
def test_validate_review_course_not_in_review_rejects(course, review, status):
    # Arrange
    course["status"] = status
    # Act
    with pytest.raises(ValueError) as error:
        validate_review(course, **review)
    # Assert
    assert str(error.value) == "REVIEW_STATUS_INVALID"


@pytest.mark.parametrize("decision", [None, "", "published", "archived", True])
def test_validate_review_unknown_decision_rejects(course, review, decision):
    # Arrange
    review["decision"] = decision
    # Act
    with pytest.raises(ValueError) as error:
        validate_review(course, **review)
    # Assert
    assert str(error.value) == "REVIEW_DECISION_INVALID"


@pytest.mark.parametrize("reason", [None, "", "   ", "x" * 9, "x" * 1001, 123])
def test_validate_review_rejection_invalid_reason_rejects(course, review, reason):
    # Arrange
    review.update(decision="rejected", reason=reason)
    # Act
    with pytest.raises(ValueError) as error:
        validate_review(course, **review)
    # Assert
    assert str(error.value) == "REVIEW_REASON_INVALID"


@pytest.mark.parametrize("reason", ["x" * 10, "x" * 1000, "  " + "x" * 10 + "  "])
def test_validate_review_rejection_valid_reason_accepts(course, review, reason):
    # Arrange
    review.update(decision="rejected", reason=reason, url_checked=False)
    # Act
    result = validate_review(course, **review)
    # Assert
    assert result == "rejected"


@pytest.mark.parametrize("url_checked", [False, None, "true", 1])
def test_validate_review_approval_without_explicit_link_check_rejects(course, review, url_checked):
    # Arrange
    review["url_checked"] = url_checked
    # Act
    with pytest.raises(ValueError) as error:
        validate_review(course, **review)
    # Assert
    assert str(error.value) == "REVIEW_URL_CHECK_REQUIRED"


@pytest.mark.parametrize("decision", ["approved", "rejected"])
def test_validate_review_valid_decision_does_not_modify_inputs(course, review, decision):
    # Arrange
    review.update(decision=decision, reason="Motivo suficientemente largo.")
    original = deepcopy((course, review))
    # Act
    validate_review(course, **review)
    # Assert
    assert (course, review) == original
