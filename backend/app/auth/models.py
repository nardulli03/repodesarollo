"""Sesiones revocables. El UUID de la fila corresponde al claim jti."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, utc_now


class AccessSession(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("expires_at > created_at", name="session_expiration"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
