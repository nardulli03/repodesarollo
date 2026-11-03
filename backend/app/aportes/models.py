"""Revisión y cambio de estado se escriben en una misma transacción."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, utc_now


class CourseReview(Base):
    __tablename__ = "course_reviews"
    __table_args__ = (
        CheckConstraint("decision IN ('approved','rejected','archived')", name="review_decision"),
        CheckConstraint("submitted_version > 0", name="review_version_positive"),
        CheckConstraint("decision != 'approved' OR url_checked_at IS NOT NULL", name="review_url_checked"),
        CheckConstraint("decision != 'rejected' OR (reason IS NOT NULL AND char_length(trim(reason)) BETWEEN 10 AND 1000)", name="review_rejection_reason"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id", ondelete="RESTRICT"), index=True)
    reviewer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    submitted_version: Mapped[int] = mapped_column(Integer)
    decision: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str | None] = mapped_column(String(1000))
    url_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
