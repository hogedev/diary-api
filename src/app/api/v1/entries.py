import datetime as dt

from fastapi import APIRouter, File, Form, Query, UploadFile

from ...domain.common import PaginatedResponse
from ...domain.entry import EntryResponse, EntryUpdate
from ..deps import CurrentUserId, EntryServiceDep

router = APIRouter()


@router.post("/", response_model=EntryResponse, status_code=201)
async def create_entry(
    service: EntryServiceDep,
    user_id: CurrentUserId,
    text: str | None = Form(default=None),  # noqa: B008
    entry_date: dt.date = Form(...),  # noqa: B008
    photos: list[UploadFile] = File(default=[]),  # noqa: B008
) -> EntryResponse:
    entry = await service.create(user_id, text, entry_date, photos)
    return EntryResponse.model_validate(entry)


@router.get("/dates", response_model=list[dt.date])
async def list_dates(
    service: EntryServiceDep,
    user_id: CurrentUserId,
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
) -> list[dt.date]:
    return await service.get_dates(user_id, year=year, month=month)


@router.get("/", response_model=PaginatedResponse[EntryResponse])
async def list_entries(
    service: EntryServiceDep,
    user_id: CurrentUserId,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    date_from: dt.date | None = Query(default=None),  # noqa: B008
    date_to: dt.date | None = Query(default=None),  # noqa: B008
) -> PaginatedResponse[EntryResponse]:
    items, total = await service.get_paginated(
        user_id, offset=offset, limit=limit, date_from=date_from, date_to=date_to
    )
    validated = [EntryResponse.model_validate(i) for i in items]
    return PaginatedResponse(items=validated, total=total, offset=offset, limit=limit)


@router.get("/{entry_id}", response_model=EntryResponse)
async def get_entry(
    entry_id: int, service: EntryServiceDep, user_id: CurrentUserId
) -> EntryResponse:
    return EntryResponse.model_validate(await service.get_by_id(entry_id, user_id))


@router.put("/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: int, data: EntryUpdate, service: EntryServiceDep, user_id: CurrentUserId
) -> EntryResponse:
    return EntryResponse.model_validate(await service.update(entry_id, user_id, data))


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(entry_id: int, service: EntryServiceDep, user_id: CurrentUserId) -> None:
    await service.delete(entry_id, user_id)


@router.post("/{entry_id}/photos", response_model=EntryResponse, status_code=201)
async def add_photos(
    entry_id: int,
    service: EntryServiceDep,
    user_id: CurrentUserId,
    photos: list[UploadFile] = File(...),  # noqa: B008
) -> EntryResponse:
    return EntryResponse.model_validate(await service.add_photos(entry_id, user_id, photos))
