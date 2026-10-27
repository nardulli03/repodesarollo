from fastapi import FastAPI

from app.cursos.router import router as courses_router

app = FastAPI(
    title="Cursos Abiertos API",
)

app.include_router(
    courses_router,
    prefix="/api/v1",
)


@app.get("/health", tags=["Estado"])
def health():
    return {"status": "ok"}