from typing import Annotated

from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/courses",
    tags=["Cursos"],
)


@router.get("")
def list_courses(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
    }