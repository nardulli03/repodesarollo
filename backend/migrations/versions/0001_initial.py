"""Esquema inicial de las entidades implementadas.

Revision ID: 0001_initial
Revises: ninguna

Migración congelada: no utiliza Base.metadata.create_all, de modo que su
resultado no depende de cambios futuros en los modelos.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("display_name", sa.String(80), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('student', 'admin')", name="user_role"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "courses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("topic", sa.String(100), nullable=True),
        sa.Column("provider", sa.String(100), nullable=True),
        sa.Column("summary", sa.String(300), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.String(2048), nullable=True),
        sa.Column("normalized_url", sa.String(2048), nullable=True),
        sa.Column("course_version", sa.String(80), nullable=True),
        sa.Column("edition_year", sa.Integer(), nullable=True),
        sa.Column("instructors", postgresql.JSONB(), nullable=False),
        sa.Column("has_quizzes", sa.Boolean(), nullable=True),
        sa.Column("requires_exam", sa.Boolean(), nullable=True),
        sa.Column("grants_certificate", sa.Boolean(), nullable=True),
        sa.Column("endorsed_by_organization", sa.Boolean(), nullable=True),
        sa.Column("organization_name", sa.String(150), nullable=True),
        sa.Column("author_has_taken", sa.Boolean(), nullable=True),
        sa.Column("language", sa.String(8), nullable=True),
        sa.Column("level", sa.String(20), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("free_content_confirmed", sa.Boolean(), nullable=True),
        sa.Column("certificate_note", sa.String(500), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('draft','in_review','published','rejected','archived')", name="course_status"),
        sa.CheckConstraint("version > 0", name="course_version_positive"),
        sa.CheckConstraint("edition_year IS NULL OR edition_year >= 1900", name="course_year_min"),
        sa.CheckConstraint("estimated_minutes IS NULL OR estimated_minutes BETWEEN 1 AND 100000", name="course_duration"),
        sa.CheckConstraint("char_length(trim(title)) BETWEEN 3 AND 150", name="course_title_length"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_url"),
    )
    op.create_index("ix_courses_created_by", "courses", ["created_by"])
    op.create_index("ix_courses_category_id", "courses", ["category_id"])
    op.create_index("ix_courses_status", "courses", ["status"])
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("expires_at > created_at", name="session_expiration"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_table(
        "course_reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("reviewer_id", sa.Uuid(), nullable=False),
        sa.Column("submitted_version", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("reason", sa.String(1000), nullable=True),
        sa.Column("url_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("decision IN ('approved','rejected','archived')", name="review_decision"),
        sa.CheckConstraint("submitted_version > 0", name="review_version_positive"),
        sa.CheckConstraint("decision != 'approved' OR url_checked_at IS NOT NULL", name="review_url_checked"),
        sa.CheckConstraint("decision != 'rejected' OR (reason IS NOT NULL AND char_length(trim(reason)) BETWEEN 10 AND 1000)", name="review_rejection_reason"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_course_reviews_course_id", "course_reviews", ["course_id"])


def downgrade():
    op.drop_table("course_reviews")
    op.drop_table("sessions")
    op.drop_table("courses")
    op.drop_table("users")
    op.drop_table("categories")
