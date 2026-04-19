from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..repositories.entry_repository import EntryRepository
from ..services.entry_service import EntryService
from ..services.storage_service import StorageService

DbSession = Annotated[AsyncSession, Depends(get_db)]

_storage: StorageService | None = None


def get_storage() -> StorageService:
    global _storage
    if _storage is None:
        _storage = StorageService()
    return _storage


def init_storage(service: StorageService) -> None:
    global _storage
    _storage = service


def get_entry_service(db: DbSession) -> EntryService:
    repo = EntryRepository(db)
    return EntryService(repo, get_storage())


EntryServiceDep = Annotated[EntryService, Depends(get_entry_service)]
