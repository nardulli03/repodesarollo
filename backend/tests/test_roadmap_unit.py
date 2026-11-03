from copy import deepcopy

import pytest

from app.roadmap.rules import add_course, move_course, remove_course


@pytest.fixture
def roadmap_items():
    return [
        {"course_id": "curso-1", "position": 1, "progress": "completed"},
        {"course_id": "curso-2", "position": 2, "progress": "in_progress"},
        {"course_id": "curso-3", "position": 3, "progress": "pending"},
    ]


def test_add_course_published_to_empty_roadmap_returns_pending_item():
    # Arrange
    items = []
    course = {"id": "curso-1", "status": "published"}

    # Act
    result = add_course(items, course)

    # Assert
    assert result == [
        {"course_id": "curso-1", "position": 1, "progress": "pending"}
    ]


def test_add_course_published_appends_after_existing_items(roadmap_items):
    # Arrange
    course = {"id": "curso-4", "status": "published"}

    # Act
    result = add_course(roadmap_items, course)

    # Assert
    assert result == roadmap_items + [
        {"course_id": "curso-4", "position": 4, "progress": "pending"}
    ]


def test_add_course_nonexistent_course_rejects(roadmap_items):
    # Arrange
    course = None

    # Act
    with pytest.raises(ValueError) as error:
        add_course(roadmap_items, course)

    # Assert
    assert str(error.value) == "ROADMAP_COURSE_NOT_FOUND"


@pytest.mark.parametrize("status", ["draft", "in_review", "rejected", "archived"])
def test_add_course_not_published_rejects(roadmap_items, status):
    # Arrange
    course = {"id": "curso-4", "status": status}

    # Act
    with pytest.raises(ValueError) as error:
        add_course(roadmap_items, course)

    # Assert
    assert str(error.value) == "ROADMAP_COURSE_NOT_PUBLISHED"


def test_add_course_already_in_roadmap_rejects(roadmap_items):
    # Arrange
    course = {"id": "curso-2", "status": "published"}

    # Act
    with pytest.raises(ValueError) as error:
        add_course(roadmap_items, course)

    # Assert
    assert str(error.value) == "ROADMAP_COURSE_DUPLICATE"


def test_add_course_reaches_limit_of_100_accepts():
    # Arrange
    items = [
        {"course_id": f"curso-{n}", "position": n, "progress": "pending"}
        for n in range(1, 100)
    ]
    course = {"id": "curso-100", "status": "published"}

    # Act
    result = add_course(items, course)

    # Assert
    assert (len(result), result[-1]) == (
        100,
        {"course_id": "curso-100", "position": 100, "progress": "pending"},
    )


def test_add_course_exceeds_limit_of_100_rejects():
    # Arrange
    items = [
        {"course_id": f"curso-{n}", "position": n, "progress": "pending"}
        for n in range(1, 101)
    ]
    course = {"id": "curso-101", "status": "published"}

    # Act
    with pytest.raises(ValueError) as error:
        add_course(items, course)

    # Assert
    assert str(error.value) == "ROADMAP_LIMIT_REACHED"


def test_add_course_does_not_modify_inputs(roadmap_items):
    # Arrange
    course = {"id": "curso-4", "status": "published"}
    original_items = deepcopy(roadmap_items)
    original_course = deepcopy(course)

    # Act
    add_course(roadmap_items, course)

    # Assert
    assert (roadmap_items, course) == (original_items, original_course)


@pytest.mark.parametrize(
    "course_id,new_position,expected_ids",
    [
        ("curso-3", 1, ["curso-3", "curso-1", "curso-2"]),
        ("curso-1", 3, ["curso-2", "curso-3", "curso-1"]),
        ("curso-1", 2, ["curso-2", "curso-1", "curso-3"]),
        ("curso-3", 2, ["curso-1", "curso-3", "curso-2"]),
        ("curso-2", 2, ["curso-1", "curso-2", "curso-3"]),
    ],
)
def test_move_course_valid_position_returns_ordered_items(
    roadmap_items, course_id, new_position, expected_ids
):
    # Arrange
    original_by_id = {item["course_id"]: item for item in roadmap_items}
    expected = [
        {**original_by_id[item_id], "position": position}
        for position, item_id in enumerate(expected_ids, start=1)
    ]

    # Act
    result = move_course(roadmap_items, course_id, new_position)

    # Assert
    assert result == expected


@pytest.mark.parametrize("position", [0, -1, 4, True, 1.5, "1", None])
def test_move_course_invalid_position_rejects(roadmap_items, position):
    # Arrange
    course_id = "curso-2"

    # Act
    with pytest.raises(ValueError) as error:
        move_course(roadmap_items, course_id, position)

    # Assert
    assert str(error.value) == "ROADMAP_POSITION_INVALID"


def test_move_course_missing_item_rejects(roadmap_items):
    # Arrange
    course_id = "curso-inexistente"

    # Act
    with pytest.raises(ValueError) as error:
        move_course(roadmap_items, course_id, 1)

    # Assert
    assert str(error.value) == "ROADMAP_ITEM_NOT_FOUND"


def test_move_course_empty_roadmap_rejects():
    # Arrange
    items = []

    # Act
    with pytest.raises(ValueError) as error:
        move_course(items, "curso-1", 1)

    # Assert
    assert str(error.value) == "ROADMAP_ITEM_NOT_FOUND"


def test_move_course_does_not_modify_input(roadmap_items):
    # Arrange
    original = deepcopy(roadmap_items)

    # Act
    move_course(roadmap_items, "curso-3", 1)

    # Assert
    assert roadmap_items == original


def test_move_course_uses_global_positions_beyond_one_page():
    # Arrange
    items = [
        {"course_id": f"curso-{n}", "position": n, "progress": "pending"}
        for n in range(1, 26)
    ]
    expected_ids = ["curso-25"] + [f"curso-{n}" for n in range(1, 25)]

    # Act
    result = move_course(items, "curso-25", 1)

    # Assert
    assert [(item["course_id"], item["position"]) for item in result] == list(
        zip(expected_ids, range(1, 26))
    )


@pytest.mark.parametrize(
    "course_id,expected_ids",
    [
        ("curso-1", ["curso-2", "curso-3"]),
        ("curso-2", ["curso-1", "curso-3"]),
        ("curso-3", ["curso-1", "curso-2"]),
    ],
)
def test_remove_course_existing_item_removes_and_reindexes(
    roadmap_items, course_id, expected_ids
):
    # Arrange
    original_by_id = {item["course_id"]: item for item in roadmap_items}
    expected = [
        {**original_by_id[item_id], "position": position}
        for position, item_id in enumerate(expected_ids, start=1)
    ]

    # Act
    result = remove_course(roadmap_items, course_id)

    # Assert
    assert result == expected


def test_remove_course_only_item_returns_empty_roadmap():
    # Arrange
    items = [{"course_id": "curso-1", "position": 1, "progress": "completed"}]

    # Act
    result = remove_course(items, "curso-1")

    # Assert
    assert result == []


def test_remove_course_missing_item_rejects(roadmap_items):
    # Arrange
    course_id = "curso-inexistente"

    # Act
    with pytest.raises(ValueError) as error:
        remove_course(roadmap_items, course_id)

    # Assert
    assert str(error.value) == "ROADMAP_ITEM_NOT_FOUND"


def test_remove_course_empty_roadmap_rejects():
    # Arrange
    items = []

    # Act
    with pytest.raises(ValueError) as error:
        remove_course(items, "curso-1")

    # Assert
    assert str(error.value) == "ROADMAP_ITEM_NOT_FOUND"


def test_remove_course_does_not_modify_input(roadmap_items):
    # Arrange
    original = deepcopy(roadmap_items)

    # Act
    remove_course(roadmap_items, "curso-2")

    # Assert
    assert roadmap_items == original


def test_add_course_removed_course_starts_pending_again(roadmap_items):
    # Arrange
    remaining = remove_course(roadmap_items, "curso-1")
    course = {"id": "curso-1", "status": "published"}

    # Act
    result = add_course(remaining, course)

    # Assert
    assert result[-1] == {
        "course_id": "curso-1",
        "position": 3,
        "progress": "pending",
    }
