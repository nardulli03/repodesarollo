def validate_review(
    course,
    *,
    reviewer_id,
    reviewer_role,
    decision,
    reason=None,
    url_checked=False,
):
    """Validar una decisión de revisión y devolver el nuevo estado.

    Función pura: no modifica el curso, no persiste ni consulta servicios.
    La identidad y el rol deben proceder de la autenticación del servidor.
    La capa de servicio debe revalidar los metadatos antes de aprobar.
    """
    if reviewer_role != "admin":
        raise ValueError("REVIEW_ADMIN_REQUIRED")

    if reviewer_id == course["created_by"]:
        raise ValueError("REVIEW_SELF_REVIEW_FORBIDDEN")

    if course["status"] != "in_review":
        raise ValueError("REVIEW_STATUS_INVALID")

    if decision not in ("approved", "rejected"):
        raise ValueError("REVIEW_DECISION_INVALID")

    if decision == "rejected":
        if not isinstance(reason, str) or not 10 <= len(reason.strip()) <= 1000:
            raise ValueError("REVIEW_REASON_INVALID")
        return "rejected"

    if url_checked is not True:
        raise ValueError("REVIEW_URL_CHECK_REQUIRED")

    return "published"
