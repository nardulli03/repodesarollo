from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.aportes.service import course_data
from app.cursos.repository import CursoRepository
from app.dependencies import get_db


router = APIRouter(prefix="/courses", tags=["Cursos"])


@router.get("")
def list_courses(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    q: Annotated[str | None, Query(max_length=100)] = None,
    category_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    result = CursoRepository(db).list(
        page=page, page_size=page_size, q=q, category_id=category_id,
    )
    return {**result, "items": [course_data(item, public=True) for item in result["items"]]}
