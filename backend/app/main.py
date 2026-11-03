from fastapi import FastAPI

from app.aportes.router import router as contributions_router
from app.auth.router import router as auth_router
from app.cursos.router import router as courses_router

app = FastAPI(title="Cursos Abiertos API")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(courses_router, prefix="/api/v1")
app.include_router(contributions_router, prefix="/api/v1")


@app.get("/health", tags=["Estado"])
def health():
    return {"status": "ok"}
