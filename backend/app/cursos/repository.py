"""Persistencia de cursos con SQLAlchemy.

Repositorio interno: el servicio valida identidad, permisos, metadatos y
transiciones antes de invocarlo. Las escrituras hacen flush; el servicio es
responsable del commit o rollback de la operación completa.
"""
from sqlalchemy import func, or_, select

from app.cursos.models import Course


UPDATE_FIELDS = frozenset({
    "category_id", "title", "topic", "provider", "summary", "description",
    "url", "normalized_url", "course_version", "edition_year", "instructors",
    "has_quizzes", "requires_exam", "grants_certificate",
    "endorsed_by_organization", "organization_name", "author_has_taken",
    "language", "level", "estimated_minutes", "free_content_confirmed",
    "certificate_note", "status",
})


class CursoRepository:
    def __init__(self, session):
        self.session = session

    def create(self, **data):
        course = Course(**data)
        self.session.add(course)
        self.session.flush()
        return course

    def get_by_id(self, course_id):
        statement = select(Course).where(
            Course.id == course_id,
            Course.status != "archived",
        )
        return self.session.scalar(statement)

    def list(self, *, page=1, page_size=20, q=None, category_id=None):
        if (
            type(page) is not int or page < 1
            or type(page_size) is not int or not 1 <= page_size <= 100
        ):
            raise ValueError("COURSE_PAGINATION_INVALID")

        filters = [Course.status == "published"]
        if q is not None:
            if not isinstance(q, str) or len(q) > 100:
                raise ValueError("COURSE_SEARCH_INVALID")
            term = q.strip()
            if term:
                filters.append(or_(
                    Course.title.icontains(term, autoescape=True),
                    Course.topic.icontains(term, autoescape=True),
                    Course.provider.icontains(term, autoescape=True),
                ))
        if category_id is not None:
            filters.append(Course.category_id == category_id)

        total = self.session.scalar(
            select(func.count()).select_from(Course).where(*filters)
        )
        statement = (
            select(Course)
            .where(*filters)
            .order_by(Course.created_at.asc(), Course.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.session.scalars(statement))
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def _get_for_update(self, course_id):
        statement = (
            select(Course)
            .where(Course.id == course_id, Course.status != "archived")
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return self.session.scalar(statement)

    def update(self, course_id, changes):
        if set(changes) - UPDATE_FIELDS:
            raise ValueError("COURSE_UPDATE_FIELD_NOT_ALLOWED")
        course = self._get_for_update(course_id)
        if course is None:
            return None
        if changes:
            for field, value in changes.items():
                setattr(course, field, value)
            course.version += 1
            self.session.flush()
        return course

    def delete(self, course_id):
        course = self._get_for_update(course_id)
        if course is None:
            return False
        course.status = "archived"
        course.version += 1
        self.session.flush()
        return True
