from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..repositories.entry_repository import EntryRepository
from ..services.auth_service import decode_token
from ..services.entry_service import EntryService
from ..services.storage_service import StorageService

DbSession = Annotated[AsyncSession, Depends(get_db)]

_storage: StorageService | None = None
_security = HTTPBearer()


def get_storage() -> StorageService:
    global _storage
    if _storage is None:
        _storage = StorageService()
    return _storage


def init_storage(service: StorageService) -> None:
    global _storage
    _storage = service


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_security),  # noqa: B008
) -> int:
    payload = decode_token(credentials.credentials)
    return int(payload["sub"])


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


def get_entry_service(db: DbSession) -> EntryService:
    repo = EntryRepository(db)
    return EntryService(repo, get_storage())


EntryServiceDep = Annotated[EntryService, Depends(get_entry_service)]
