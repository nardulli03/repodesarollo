"""Casos de uso de aportes. El servidor deriva autor y revisor de la sesión."""
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.aportes.models import CourseReview
from app.aportes.rules import validate_review
from app.aportes.schemas import CourseDraft
from app.cursos.models import Course
from app.cursos.repository import CursoRepository
from app.cursos.rules import normalize_course_url, transition_course, validate_course_contribution
from app.database import Category


EDITORIAL_FIELDS = tuple(CourseDraft.model_fields)


def course_data(course, *, public=False):
    data = {field: getattr(course, field) for field in EDITORIAL_FIELDS}
    data.update(id=course.id, status=course.status)
    if public:
        data.pop("author_has_taken", None)
    else:
        data.update(created_by=course.created_by, version=course.version)
    return data


def _error(status, code):
    return HTTPException(status, detail={"code": code})


def _check_category(db, category_id):
    if category_id is not None and db.get(Category, category_id) is None:
        raise _error(422, "COURSE_CATEGORY_NOT_FOUND")


def _check_complete(db, course):
    data = {field: getattr(course, field) for field in EDITORIAL_FIELDS}
    if data["category_id"] is not None:
        data["category_id"] = str(data["category_id"])
    existing = db.scalars(select(Course.normalized_url).where(
        Course.id != course.id, Course.normalized_url.is_not(None),
    )).all()
    try:
        validate_course_contribution(
            data, current_year=datetime.now(timezone.utc).year, existing_urls=existing,
        )
    except ValueError as error:
        code = str(error)
        raise _error(409 if code == "COURSE_URL_DUPLICATE" else 422, code) from None
    _check_category(db, course.category_id)
    return normalize_course_url(course.url)


def _locked_course(db, course_id, *, owner_id=None):
    query = select(Course).where(Course.id == course_id)
    if owner_id is not None:
        query = query.where(Course.created_by == owner_id)
    course = db.scalar(query.with_for_update().execution_options(populate_existing=True))
    if course is None:
        raise _error(404, "COURSE_NOT_FOUND")
    return course


def _check_version(course, expected):
    if course.version != expected:
        raise _error(409, "COURSE_VERSION_CONFLICT")


def _commit(db):
    try:
        db.flush()
        db.commit()
    except IntegrityError as error:
        db.rollback()
        code = getattr(error.orig, "sqlstate", None)
        if code == "23505":
            raise _error(409, "COURSE_URL_DUPLICATE") from None
        raise _error(422, "COURSE_DATA_INVALID") from None


def create_draft(db, actor, payload):
    data = payload.model_dump()
    _check_category(db, data["category_id"])
    if data["url"] is not None:
        data["normalized_url"] = normalize_course_url(data["url"])
        duplicate = db.scalar(select(Course.id).where(Course.normalized_url == data["normalized_url"]))
        if duplicate is not None:
            raise _error(409, "COURSE_URL_DUPLICATE")
    try:
        course = CursoRepository(db).create(**data, created_by=actor.id, status="draft")
    except IntegrityError as error:
        db.rollback()
        if getattr(error.orig, "sqlstate", None) == "23505":
            raise _error(409, "COURSE_URL_DUPLICATE") from None
        raise _error(422, "COURSE_DATA_INVALID") from None
    _commit(db)
    return course


def submit_course(db, actor, course_id, expected_version):
    course = _locked_course(db, course_id, owner_id=actor.id)
    _check_version(course, expected_version)
    if course.status != "draft":
        raise _error(409, "COURSE_SUBMIT_STATUS_INVALID")
    normalized = _check_complete(db, course)
    course.normalized_url = normalized
    course.status = transition_course(course.status, "in_review")
    course.version += 1
    _commit(db)
    return course


def review_course(db, actor, course_id, payload):
    course = _locked_course(db, course_id)
    _check_version(course, payload.expected_version)
    decision = "approved" if payload.approved else "rejected"
    try:
        status = validate_review(
            {"created_by": course.created_by, "status": course.status},
            reviewer_id=actor.id, reviewer_role=actor.role, decision=decision,
            reason=payload.reason, url_checked=payload.url_checked,
        )
    except ValueError as error:
        code = str(error)
        if code in ("REVIEW_ADMIN_REQUIRED", "REVIEW_SELF_REVIEW_FORBIDDEN"):
            raise _error(403, code) from None
        raise _error(409 if code == "REVIEW_STATUS_INVALID" else 422, code) from None
    if payload.approved:
        course.normalized_url = _check_complete(db, course)
    now = datetime.now(timezone.utc)
    review = CourseReview(
        course_id=course.id, reviewer_id=actor.id, submitted_version=course.version,
        decision=decision, reason=payload.reason.strip() if payload.reason else None,
        url_checked_at=now if payload.approved else None, reviewed_at=now,
    )
    course.status = transition_course(course.status, status)
    course.version += 1
    db.add(review)
    _commit(db)
    return course
