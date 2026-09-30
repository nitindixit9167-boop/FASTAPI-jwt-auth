from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (registers tables)
from app.core.config import settings
from app.db import Base, engine
from app.routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # use Alembic migrations in production
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Reference FastAPI service with OAuth2 password flow and JWT access/refresh tokens.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
