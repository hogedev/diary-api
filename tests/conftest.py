"""テストフィクスチャ"""

from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.app.api.deps import init_storage
from src.app.database import get_db
from src.app.main import app
from src.app.models.base import Base


@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession]:
    session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session


@pytest.fixture(scope="function")
def mock_storage():
    mock = MagicMock()
    mock.ensure_dir = MagicMock()
    mock.upload = AsyncMock()
    mock.get = AsyncMock(return_value=b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    mock.delete = AsyncMock()
    mock.delete_many = AsyncMock()
    return mock


@pytest.fixture(scope="function")
def client(test_engine, mock_storage) -> Generator[TestClient]:
    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        init_storage(mock_storage)
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_header(client) -> dict[str, str]:
    """テスト用ユーザーを作成しAuthorizationヘッダを返す"""
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "testpass"},
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_image() -> bytes:
    """100x100 赤ピクセルのJPEG"""
    import io

    from PIL import Image

    img = Image.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()
