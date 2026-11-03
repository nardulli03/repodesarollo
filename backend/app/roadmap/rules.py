MAX_ROADMAP_COURSES = 100


def _reindex(items):
    """Crear una nueva lista con posiciones consecutivas desde 1."""
    return [
        {**item, "position": position}
        for position, item in enumerate(items, start=1)
    ]


def _find_index(items, course_id):
    """Buscar un curso dentro del roadmap."""
    for index, item in enumerate(items):
        if item["course_id"] == course_id:
            return index

    raise ValueError("ROADMAP_ITEM_NOT_FOUND")


def add_course(items, course):
    """Agregar un curso publicado sin modificar los datos recibidos."""
    if course is None:
        raise ValueError("ROADMAP_COURSE_NOT_FOUND")

    if course["status"] != "published":
        raise ValueError("ROADMAP_COURSE_NOT_PUBLISHED")

    course_id = course["id"]

    if any(item["course_id"] == course_id for item in items):
        raise ValueError("ROADMAP_COURSE_DUPLICATE")

    if len(items) >= MAX_ROADMAP_COURSES:
        raise ValueError("ROADMAP_LIMIT_REACHED")

    new_item = {
        "course_id": course_id,
        "position": len(items) + 1,
        "progress": "pending",
    }

    return _reindex([*items, new_item])


def move_course(items, course_id, new_position):
    """Mover un curso conservando su progreso y el de los demás."""
    current_index = _find_index(items, course_id)

    if (
        type(new_position) is not int
        or not 1 <= new_position <= len(items)
    ):
        raise ValueError("ROADMAP_POSITION_INVALID")

    reordered = list(items)
    moved_item = reordered.pop(current_index)
    reordered.insert(new_position - 1, moved_item)

    return _reindex(reordered)


def remove_course(items, course_id):
    """Quitar un curso y reorganizar las posiciones restantes."""
    current_index = _find_index(items, course_id)

    remaining = list(items)
    remaining.pop(current_index)

    return _reindex(remaining)