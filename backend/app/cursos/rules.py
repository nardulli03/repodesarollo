from urllib.parse import urlsplit, urlunsplit


def normalize_course_url(url):
    """Validar y normalizar una URL sin acceder a Internet."""
    if not isinstance(url, str):
        raise ValueError("COURSE_URL_INVALID")

    url = url.strip()

    if (
        not url
        or len(url) > 2048
        or any(character.isspace() or ord(character) < 32 for character in url)
        or "\\" in url
    ):
        raise ValueError("COURSE_URL_INVALID")

    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port

        if (
            parsed.scheme.lower() != "https"
            or not hostname
            or parsed.username is not None
            or parsed.password is not None
            or (port is not None and not 1 <= port <= 65535)
        ):
            raise ValueError("COURSE_URL_INVALID")

    except ValueError:
        raise ValueError("COURSE_URL_INVALID") from None

    hostname = hostname.lower()
    if ":" in hostname:
        hostname = f"[{hostname}]"

    netloc = hostname
    if port is not None and port != 443:
        netloc = f"{hostname}:{port}"

    return urlunsplit(("https", netloc, parsed.path, parsed.query, ""))


def _required_text(data, field):
    """Obtener texto no vacío sin modificar el diccionario recibido."""
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        code = (
            "COURSE_TITLE_REQUIRED"
            if field == "title"
            else f"COURSE_FIELD_REQUIRED:{field}"
        )
        raise ValueError(code)
    return value.strip()


def _check_text_length(value, field, minimum, maximum):
    if not minimum <= len(value) <= maximum:
        raise ValueError(f"COURSE_FIELD_LENGTH:{field}")


def validate_course_contribution(data, *, current_year, existing_urls):
    """Validar un aporte completo sin BD, HTTP, reloj ni mutaciones.

    current_year se entrega explícitamente para mantener repetibilidad.
    existing_urls contiene URLs válidas de otros cursos; al editar, el
    servicio debe excluir la URL del propio curso. La base de datos debe
    reforzar la unicidad para evitar altas concurrentes duplicadas.
    La existencia de categoría y los permisos se verifican en sus servicios.
    """
    text_limits = {
        "title": (3, 150),
        "topic": (2, 100),
        "provider": (2, 100),
        "summary": (20, 300),
        "description": (50, 10000),
    }
    for field, (minimum, maximum) in text_limits.items():
        value = _required_text(data, field)
        _check_text_length(value, field, minimum, maximum)

    _required_text(data, "category_id")
    language = _required_text(data, "language")
    level = _required_text(data, "level")

    if language not in {"es", "en", "pt"}:
        raise ValueError("COURSE_LANGUAGE_INVALID")
    if level not in {"inicial", "intermedio", "avanzado"}:
        raise ValueError("COURSE_LEVEL_INVALID")

    boolean_fields = (
        "has_quizzes",
        "requires_exam",
        "grants_certificate",
        "endorsed_by_organization",
        "author_has_taken",
        "free_content_confirmed",
    )
    for field in boolean_fields:
        # En Python bool es una subclase de int; se exige bool exacto.
        if type(data.get(field)) is not bool:
            raise ValueError(f"COURSE_FLAG_INVALID:{field}")

    if not data["free_content_confirmed"]:
        raise ValueError("COURSE_NOT_FREE")

    organization_name = data.get("organization_name")
    if data["endorsed_by_organization"]:
        if (
            not isinstance(organization_name, str)
            or not organization_name.strip()
        ):
            raise ValueError("COURSE_ORGANIZATION_REQUIRED")
        _check_text_length(
            organization_name.strip(), "organization_name", 2, 150
        )
    elif organization_name is not None:
        raise ValueError("COURSE_ORGANIZATION_UNEXPECTED")

    edition_year = data.get("edition_year")
    if edition_year is not None:
        if (
            type(edition_year) is not int
            or edition_year < 1900
            or edition_year > current_year
        ):
            raise ValueError("COURSE_YEAR_INVALID")

    minutes = data.get("estimated_minutes")
    if type(minutes) is not int or not 1 <= minutes <= 100000:
        raise ValueError("COURSE_DURATION_INVALID")

    course_version = data.get("course_version")
    if course_version is not None:
        if (
            not isinstance(course_version, str)
            or not 1 <= len(course_version.strip()) <= 80
        ):
            raise ValueError("COURSE_VERSION_INVALID")

    instructors = data.get("instructors")
    if not isinstance(instructors, list) or len(instructors) > 20:
        raise ValueError("COURSE_INSTRUCTORS_INVALID")
    for instructor in instructors:
        if (
            not isinstance(instructor, str)
            or not 2 <= len(instructor.strip()) <= 120
        ):
            raise ValueError("COURSE_INSTRUCTORS_INVALID")

    certificate_note = data.get("certificate_note")
    if certificate_note is not None:
        if (
            not isinstance(certificate_note, str)
            or len(certificate_note.strip()) > 500
        ):
            raise ValueError("COURSE_CERTIFICATE_NOTE_INVALID")

    normalized_url = normalize_course_url(data.get("url"))
    normalized_existing_urls = {
        normalize_course_url(existing_url)
        for existing_url in existing_urls
    }
    if normalized_url in normalized_existing_urls:
        raise ValueError("COURSE_URL_DUPLICATE")

    return None


def transition_course(current_status, new_status):
    """Validar el cambio de estado, sin comprobar permisos del actor."""
    allowed_transitions = {
        "draft": {"in_review", "archived"},
        "in_review": {"published", "rejected", "archived"},
        "rejected": {"draft", "archived"},
        "published": {"draft", "archived"},
        "archived": set(),
    }

    allowed_destinations = allowed_transitions.get(current_status, set())
    if new_status not in allowed_destinations:
        raise ValueError("COURSE_TRANSITION_NOT_ALLOWED")

    return new_status
