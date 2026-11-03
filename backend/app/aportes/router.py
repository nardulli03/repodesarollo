from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.aportes.schemas import CourseDraft, ReviewRequest, SubmitRequest
from app.aportes.service import course_data, create_draft, review_course, submit_course
from app.auth.csrf import require_csrf
from app.auth.dependencies import get_admin_user, get_current_user
from app.database import User
from app.dependencies import get_db


router = APIRouter(tags=["Aportes"])


@router.post("/me/courses", status_code=201)
def create(
    payload: CourseDraft, response: Response,
    actor: User = Depends(get_current_user),
    csrf=Depends(require_csrf), db: Session = Depends(get_db),
):
    course = create_draft(db, actor, payload)
    response.headers["Location"] = f"/api/v1/me/courses/{course.id}"
    response.headers["Cache-Control"] = "no-store"
    return course_data(course)


@router.post("/me/courses/{course_id}/submit")
def submit(
    course_id: UUID, payload: SubmitRequest, response: Response,
    actor: User = Depends(get_current_user),
    csrf=Depends(require_csrf), db: Session = Depends(get_db),
):
    course = submit_course(db, actor, course_id, payload.expected_version)
    response.headers["Cache-Control"] = "no-store"
    return course_data(course)


@router.post("/admin/reviews/{course_id}/decision")
def decide(
    course_id: UUID, payload: ReviewRequest, response: Response,
    actor: User = Depends(get_admin_user),
    csrf=Depends(require_csrf), db: Session = Depends(get_db),
):
    course = review_course(db, actor, course_id, payload)
    response.headers["Cache-Control"] = "no-store"
    return course_data(course)
