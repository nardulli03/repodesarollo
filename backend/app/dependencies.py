"""Conexión de aplicación. Las pruebas reemplazan solo esta dependencia."""
import os
from functools import lru_cache

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


@lru_cache(maxsize=4)
def _engine_for_url(url):
    return create_engine(url, pool_pre_ping=True)


def get_db():
    value = os.environ.get("DATABASE_URL")
    if not value:
        raise HTTPException(503, detail={"code": "DATABASE_NOT_CONFIGURED"})
    with Session(_engine_for_url(value)) as session:
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise HTTPException(503, detail={"code": "DATABASE_UNAVAILABLE"}) from None
        except Exception:
            session.rollback()
            raise
