import asyncio
import io
import logging
from functools import partial

from minio import Minio

from ..config import settings

logger = logging.getLogger(__name__)


class MinioService:
    def __init__(self) -> None:
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket = settings.minio_bucket

    async def ensure_bucket(self) -> None:
        loop = asyncio.get_running_loop()
        exists = await loop.run_in_executor(None, self.client.bucket_exists, self.bucket)
        if not exists:
            await loop.run_in_executor(None, self.client.make_bucket, self.bucket)
            logger.info("Created MinIO bucket: %s", self.bucket)

    async def upload(self, key: str, data: bytes, content_type: str) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            partial(
                self.client.put_object,
                self.bucket,
                key,
                io.BytesIO(data),
                len(data),
                content_type=content_type,
            ),
        )

    async def get(self, key: str) -> bytes:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, partial(self.client.get_object, self.bucket, key)
        )
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    async def delete(self, key: str) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, partial(self.client.remove_object, self.bucket, key))

    async def delete_many(self, keys: list[str]) -> None:
        for key in keys:
            await self.delete(key)
