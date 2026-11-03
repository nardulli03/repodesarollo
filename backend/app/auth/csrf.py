"""Cookie firmada + header coincidente + Origin exacto para mutaciones."""
import hmac
import os
from datetime import datetime, timezone
from uuid import UUID, uuid4

import jwt
from fastapi import HTTPException, Request, Response


CSRF_LIFETIME = 43200


def cookie_secure():
    return os.environ.get("COOKIE_SECURE", "false").lower() == "true"


def csrf_cookie_name():
    return "__Host-csrf_token" if cookie_secure() else "csrf_token_dev"


def _signing_key():
    key = os.environ.get("CSRF_SIGNING_KEY", "")
    if len(key.encode("utf-8")) < 32 or key == os.environ.get("JWT_SIGNING_KEY"):
        raise HTTPException(503, detail={"code": "CSRF_NOT_CONFIGURED"})
    return key


def issue_csrf(response: Response):
    now = int(datetime.now(timezone.utc).timestamp())
    token = jwt.encode({
        "purpose": "csrf", "nonce": str(uuid4()),
        "iat": now, "exp": now + CSRF_LIFETIME,
    }, _signing_key(), algorithm="HS256")
    response.set_cookie(
        csrf_cookie_name(), token, max_age=CSRF_LIFETIME,
        httponly=False, secure=cookie_secure(), samesite="lax", path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    return {"csrf_token": token}


def require_csrf(request: Request):
    origin = os.environ.get("FRONTEND_ORIGIN", "")
    if not origin:
        raise HTTPException(503, detail={"code": "ORIGIN_NOT_CONFIGURED"})
    if request.headers.get("Origin") != origin:
        raise HTTPException(403, detail={"code": "CSRF_INVALID"})

    cookie = request.cookies.get(csrf_cookie_name(), "")
    header = request.headers.get("X-CSRF-Token", "")
    if (
        not cookie or not header or len(cookie) > 4096 or len(header) > 4096
        or not hmac.compare_digest(cookie.encode(), header.encode())
    ):
        raise HTTPException(403, detail={"code": "CSRF_INVALID"})
    key = _signing_key()
    try:
        data = jwt.decode(
            cookie, key, algorithms=["HS256"],
            options={"require": ["purpose", "nonce", "iat", "exp"]},
        )
        if data["purpose"] != "csrf":
            raise ValueError("Wrong purpose")
        UUID(data["nonce"])
        if (
            type(data["iat"]) is not int or type(data["exp"]) is not int
            or not 0 < data["exp"] - data["iat"] <= CSRF_LIFETIME
        ):
            raise ValueError("Invalid lifetime")
    except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError):
        raise HTTPException(403, detail={"code": "CSRF_INVALID"}) from None
