from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..repositories.entry_repository import EntryRepository
from ..services.entry_service import EntryService
from ..services.minio_service import MinioService

DbSession = Annotated[AsyncSession, Depends(get_db)]

_minio: MinioService | None = None


def get_minio() -> MinioService:
    global _minio
    if _minio is None:
        _minio = MinioService()
    return _minio


def init_minio(service: MinioService) -> None:
    global _minio
    _minio = service


def get_entry_service(db: DbSession) -> EntryService:
    repo = EntryRepository(db)
    return EntryService(repo, get_minio())


EntryServiceDep = Annotated[EntryService, Depends(get_entry_service)]
