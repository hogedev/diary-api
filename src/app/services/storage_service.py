import logging
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self) -> None:
        self.base_path = Path(settings.photos_dir)

    def ensure_dir(self) -> None:
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info("Photos directory: %s", self.base_path)

    async def upload(self, key: str, data: bytes, content_type: str) -> None:
        path = self.base_path / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    async def get(self, key: str) -> bytes:
        path = self.base_path / key
        return path.read_bytes()

    async def delete(self, key: str) -> None:
        path = self.base_path / key
        if path.exists():
            path.unlink()

    async def delete_many(self, keys: list[str]) -> None:
        for key in keys:
            await self.delete(key)
