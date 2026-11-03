"""Validación de JWT de cookie y autorización basada en el usuario actual.

No emite tokens ni implementa login. El rol se obtiene de PostgreSQL, no
se acepta desde headers del cliente ni desde un claim de rol.
"""
import os
from datetime import datetime, timezone
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth.models import AccessSession
from app.database import User
from app.dependencies import get_db


REQUIRED_CLAIMS = ("sub", "jti", "iss", "aud", "iat", "nbf", "exp")


def access_cookie_name():
    if os.environ.get("COOKIE_SECURE", "false").lower() == "true":
        return "__Host-access_token"
    return "access_token_dev"


def _unauthorized():
    return HTTPException(401, detail={"code": "AUTH_REQUIRED"})


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(access_cookie_name())
    if not token:
        raise _unauthorized()

    key = os.environ.get("JWT_SIGNING_KEY", "")
    issuer = os.environ.get("JWT_ISSUER", "")
    audience = os.environ.get("JWT_AUDIENCE", "")
    if len(key.encode("utf-8")) < 32 or not issuer or not audience:
        raise HTTPException(503, detail={"code": "AUTH_NOT_CONFIGURED"})

    try:
        claims = jwt.decode(
            token, key, algorithms=["HS256"], issuer=issuer, audience=audience,
            leeway=30, options={"require": list(REQUIRED_CLAIMS)},
        )
        user_id = UUID(claims["sub"])
        session_id = UUID(claims["jti"])
        if any(type(claims[name]) is not int for name in ("iat", "nbf", "exp")):
            raise ValueError("Invalid claim type")
        if not (
            claims["iat"] <= claims["nbf"] < claims["exp"]
            and 0 < claims["exp"] - claims["iat"] <= 900
        ):
            raise ValueError("Invalid lifetime")
    except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError):
        raise _unauthorized() from None

    now = datetime.now(timezone.utc)
    session = db.get(AccessSession, session_id, populate_existing=True)
    if (
        session is None or session.user_id != user_id
        or session.revoked_at is not None or session.expires_at <= now
    ):
        raise _unauthorized()

    user = db.get(User, user_id, populate_existing=True)
    if user is None or not user.is_active:
        raise _unauthorized()
    if user.email_verified_at is None:
        raise HTTPException(403, detail={"code": "EMAIL_NOT_VERIFIED"})
    return user


def get_admin_user(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, detail={"code": "ADMIN_REQUIRED"})
    return user
