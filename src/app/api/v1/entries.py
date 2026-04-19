import datetime as dt

from fastapi import APIRouter, File, Form, Query, UploadFile

from ...domain.common import PaginatedResponse
from ...domain.entry import EntryResponse, EntryUpdate
from ..deps import EntryServiceDep

router = APIRouter()


@router.post("/", response_model=EntryResponse, status_code=201)
async def create_entry(
    service: EntryServiceDep,
    text: str | None = Form(default=None),  # noqa: B008
    entry_date: dt.date = Form(...),  # noqa: B008
    photos: list[UploadFile] = File(default=[]),  # noqa: B008
):
    entry = await service.create(text, entry_date, photos)
    return entry


@router.get("/dates", response_model=list[dt.date])
async def list_dates(
    service: EntryServiceDep,
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
):
    return await service.get_dates(year=year, month=month)


@router.get("/", response_model=PaginatedResponse[EntryResponse])
async def list_entries(
    service: EntryServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    date_from: dt.date | None = Query(default=None),  # noqa: B008
    date_to: dt.date | None = Query(default=None),  # noqa: B008
):
    items, total = await service.get_paginated(
        offset=offset, limit=limit, date_from=date_from, date_to=date_to
    )
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)


@router.get("/{entry_id}", response_model=EntryResponse)
async def get_entry(entry_id: int, service: EntryServiceDep):
    return await service.get_by_id(entry_id)


@router.put("/{entry_id}", response_model=EntryResponse)
async def update_entry(entry_id: int, data: EntryUpdate, service: EntryServiceDep):
    return await service.update(entry_id, data)


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(entry_id: int, service: EntryServiceDep):
    await service.delete(entry_id)


@router.post("/{entry_id}/photos", response_model=EntryResponse, status_code=201)
async def add_photos(
    entry_id: int,
    service: EntryServiceDep,
    photos: list[UploadFile] = File(...),  # noqa: B008
):
    return await service.add_photos(entry_id, photos)
