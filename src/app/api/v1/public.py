import datetime as dt

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from ...domain.common import PaginatedResponse
from ...domain.entry import EntryResponse
from ..deps import EntryServiceDep, get_storage

router = APIRouter()


@router.get("/entries", response_model=PaginatedResponse[EntryResponse])
async def list_public_entries(
    service: EntryServiceDep,
    username: str | None = Query(default=None),  # noqa: B008
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    date_from: dt.date | None = Query(default=None),  # noqa: B008
    date_to: dt.date | None = Query(default=None),  # noqa: B008
) -> PaginatedResponse[EntryResponse]:
    items, total = await service.repository.get_public_paginated(
        username=username,
        offset=offset,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
    )
    validated = [EntryResponse.model_validate(i) for i in items]
    return PaginatedResponse(items=validated, total=total, offset=offset, limit=limit)


@router.get("/entries/dates", response_model=list[dt.date])
async def list_public_dates(
    service: EntryServiceDep,
    username: str | None = Query(default=None),  # noqa: B008
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
) -> list[dt.date]:
    return await service.repository.get_public_dates(
        username=username,
        year=year,
        month=month,
    )


@router.get("/entries/{entry_id}", response_model=EntryResponse)
async def get_public_entry(entry_id: int, service: EntryServiceDep) -> EntryResponse:
    entry = await service.repository.get_public_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return EntryResponse.model_validate(entry)


@router.get("/photos/{photo_id}/image")
async def get_public_photo(
    photo_id: int,
    service: EntryServiceDep,
    w: int | None = Query(default=None),  # noqa: B008
) -> Response:
    from ...models.photo import Photo

    photo = await service.repository.session.get(Photo, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    # 公開エントリの写真かチェック
    entry = await service.repository.get_public_by_id(photo.entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Photo not found")
    thumb = w is not None and w <= 800
    key = photo.thumb_key if thumb and photo.thumb_key else photo.object_key
    ct = "image/jpeg" if thumb and photo.thumb_key else (photo.content_type or "image/jpeg")
    storage = get_storage()
    data = await storage.get(key)
    return Response(
        content=data,
        media_type=ct,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
