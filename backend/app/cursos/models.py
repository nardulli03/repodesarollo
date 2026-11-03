"""Persistencia de cursos; las reglas completas de envío siguen en rules.py."""
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, Timestamps


class Course(Timestamps, Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("status IN ('draft','in_review','published','rejected','archived')", name="course_status"),
        CheckConstraint("version > 0", name="course_version_positive"),
        CheckConstraint("edition_year IS NULL OR edition_year >= 1900", name="course_year_min"),
        CheckConstraint("estimated_minutes IS NULL OR estimated_minutes BETWEEN 1 AND 100000", name="course_duration"),
        CheckConstraint("char_length(trim(title)) BETWEEN 3 AND 150", name="course_title_length"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    category_id: Mapped[UUID | None] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True)
    title: Mapped[str] = mapped_column(String(150))
    topic: Mapped[str | None] = mapped_column(String(100))
    provider: Mapped[str | None] = mapped_column(String(100))
    summary: Mapped[str | None] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(String(2048))
    normalized_url: Mapped[str | None] = mapped_column(String(2048), unique=True)
    course_version: Mapped[str | None] = mapped_column(String(80))
    edition_year: Mapped[int | None] = mapped_column(Integer)
    instructors: Mapped[list[str]] = mapped_column(JSONB, default=list)
    has_quizzes: Mapped[bool | None] = mapped_column(Boolean)
    requires_exam: Mapped[bool | None] = mapped_column(Boolean)
    grants_certificate: Mapped[bool | None] = mapped_column(Boolean)
    endorsed_by_organization: Mapped[bool | None] = mapped_column(Boolean)
    organization_name: Mapped[str | None] = mapped_column(String(150))
    author_has_taken: Mapped[bool | None] = mapped_column(Boolean)
    language: Mapped[str | None] = mapped_column(String(8))
    level: Mapped[str | None] = mapped_column(String(20))
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    free_content_confirmed: Mapped[bool | None] = mapped_column(Boolean)
    certificate_note: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
