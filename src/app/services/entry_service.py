import datetime as dt

from fastapi import UploadFile

from ..domain.entry import EntryUpdate
from ..exceptions import AppError, NotFoundError
from ..models.entry import Entry
from ..repositories.entry_repository import EntryRepository
from . import photo_service
from .storage_service import StorageService


class EntryService:
    def __init__(self, repository: EntryRepository, storage: StorageService):
        self.repository = repository
        self.storage = storage

    async def get_paginated(
        self,
        user_id: int,
        *,
        offset: int = 0,
        limit: int = 20,
        date_from: dt.date | None = None,
        date_to: dt.date | None = None,
    ) -> tuple[list[Entry], int]:
        return await self.repository.get_paginated_by_date(
            user_id, offset=offset, limit=limit, date_from=date_from, date_to=date_to
        )

    async def get_by_id(self, entry_id: int, user_id: int) -> Entry:
        entry = await self.repository.get_by_id_for_user(entry_id, user_id)
        if not entry:
            raise NotFoundError("Entry", entry_id)
        return entry

    async def get_dates(
        self, user_id: int, *, year: int | None = None, month: int | None = None
    ) -> list[dt.date]:
        return await self.repository.get_dates(user_id, year=year, month=month)

    async def create(
        self,
        user_id: int,
        text: str | None,
        entry_date: dt.date,
        photos: list[UploadFile],
    ) -> Entry:
        entry = Entry(user_id=user_id, text=text, entry_date=entry_date)
        entry = await self.repository.create(entry)

        for upload in photos:
            data = await upload.read()
            if not data:
                continue
            photo, original, thumb = photo_service.process_upload(
                data, upload.filename, upload.content_type, entry_date
            )
            await self.storage.upload(
                photo.object_key, original, photo.content_type or "image/jpeg"
            )
            if thumb and photo.thumb_key:
                await self.storage.upload(photo.thumb_key, thumb, "image/jpeg")
            photo.entry_id = entry.id
            entry.photos.append(photo)

        await self.repository.update(entry)
        return entry

    async def update(self, entry_id: int, user_id: int, data: EntryUpdate) -> Entry:
        entry = await self.get_by_id(entry_id, user_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(entry, key, value)
        return await self.repository.update(entry)

    async def delete(self, entry_id: int, user_id: int) -> None:
        entry = await self.get_by_id(entry_id, user_id)
        keys = []
        for photo in entry.photos:
            keys.append(photo.object_key)
            if photo.thumb_key:
                keys.append(photo.thumb_key)
        if keys:
            await self.storage.delete_many(keys)
        await self.repository.delete(entry)

    async def add_photos(self, entry_id: int, user_id: int, photos: list[UploadFile]) -> Entry:
        entry = await self.get_by_id(entry_id, user_id)
        for upload in photos:
            data = await upload.read()
            if not data:
                continue
            photo, original, thumb = photo_service.process_upload(
                data, upload.filename, upload.content_type, entry.entry_date
            )
            await self.storage.upload(
                photo.object_key, original, photo.content_type or "image/jpeg"
            )
            if thumb and photo.thumb_key:
                await self.storage.upload(photo.thumb_key, thumb, "image/jpeg")
            photo.entry_id = entry.id
            entry.photos.append(photo)
        await self.repository.update(entry)
        return entry

    async def delete_photo(self, photo_id: int, user_id: int) -> None:
        from ..models.photo import Photo

        photo = await self.repository.session.get(Photo, photo_id)
        if not photo:
            raise NotFoundError("Photo", photo_id)
        # 所有権チェック
        entry = await self.repository.get_by_id_for_user(photo.entry_id, user_id)
        if not entry:
            raise AppError("Permission denied", 403)
        await self.storage.delete(photo.object_key)
        if photo.thumb_key:
            await self.storage.delete(photo.thumb_key)
        await self.repository.session.delete(photo)

    async def get_photo_data(
        self, photo_id: int, user_id: int, thumb: bool = False
    ) -> tuple[bytes, str]:
        from ..models.photo import Photo

        photo = await self.repository.session.get(Photo, photo_id)
        if not photo:
            raise NotFoundError("Photo", photo_id)
        entry = await self.repository.get_by_id_for_user(photo.entry_id, user_id)
        if not entry:
            raise AppError("Permission denied", 403)
        key = photo.thumb_key if thumb and photo.thumb_key else photo.object_key
        ct = "image/jpeg" if thumb and photo.thumb_key else (photo.content_type or "image/jpeg")
        data = await self.storage.get(key)
        return data, ct
