import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from .api.deps import init_minio
from .api.v1 import router as api_router
from .config import settings
from .exceptions import AppError
from .middleware.logging import RequestLoggingMiddleware
from .services.minio_service import MinioService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # DB ディレクトリ確保
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
    if db_path and not db_path.startswith(":"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    # テーブル作成
    from .database import engine
    from .models import Entry, Photo  # noqa: F401
    from .models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # MinIO 初期化
    minio = MinioService()
    init_minio(minio)
    try:
        await minio.ensure_bucket()
    except Exception:
        logger.warning("MinIO not available at startup, will retry on first request")

    yield


app = FastAPI(
    title="Diary API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/", include_in_schema=False)
async def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
