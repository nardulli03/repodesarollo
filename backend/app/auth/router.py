from fastapi import APIRouter, Depends, Response

from app.auth.csrf import issue_csrf
from app.auth.dependencies import get_current_user
from app.database import User


router = APIRouter(prefix="/auth", tags=["Identidad"])


@router.get("/csrf")
def csrf(response: Response):
    return issue_csrf(response)


@router.get("/me")
def me(response: Response, user: User = Depends(get_current_user)):
    response.headers["Cache-Control"] = "no-store"
    return {
        "id": str(user.id), "display_name": user.display_name,
        "email": user.email, "role": user.role,
        "email_verified_at": user.email_verified_at,
    }
