from datetime import datetime, timezone
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StringConstraints, field_validator

from app.cursos.rules import normalize_course_url


Title = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=3, max_length=150)]
Name = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=2, max_length=100)]
Instructor = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=2, max_length=120)]


class CourseDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Title
    category_id: UUID | None = None
    topic: Name | None = None
    provider: Name | None = None
    summary: Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=20, max_length=300)] | None = None
    description: Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=50, max_length=10000)] | None = None
    url: str | None = None
    course_version: Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=80)] | None = None
    edition_year: Annotated[int, Field(strict=True, ge=1900)] | None = None
    instructors: Annotated[list[Instructor], Field(max_length=20)] = Field(default_factory=list)
    has_quizzes: StrictBool | None = None
    requires_exam: StrictBool | None = None
    grants_certificate: StrictBool | None = None
    endorsed_by_organization: StrictBool | None = None
    organization_name: Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=2, max_length=150)] | None = None
    author_has_taken: StrictBool | None = None
    language: Literal["es", "en", "pt"] | None = None
    level: Literal["inicial", "intermedio", "avanzado"] | None = None
    estimated_minutes: Annotated[int, Field(strict=True, ge=1, le=100000)] | None = None
    free_content_confirmed: StrictBool | None = None
    certificate_note: Annotated[str, StringConstraints(strict=True, max_length=500)] | None = None

    @field_validator("url")
    @classmethod
    def valid_url(cls, value):
        if value is not None:
            normalize_course_url(value)
            return value.strip()
        return None

    @field_validator("edition_year")
    @classmethod
    def valid_year(cls, value):
        if value is not None and value > datetime.now(timezone.utc).year:
            raise ValueError("COURSE_YEAR_INVALID")
        return value


class SubmitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: Annotated[int, Field(strict=True, ge=1)]


class ReviewRequest(SubmitRequest):
    approved: StrictBool
    reason: Annotated[str, StringConstraints(strict=True, max_length=1000)] | None = None
    url_checked: StrictBool = False
