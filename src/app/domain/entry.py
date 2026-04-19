import datetime as dt

from pydantic import BaseModel


class EntryUpdate(BaseModel):
    text: str | None = None
    entry_date: dt.date | None = None


class PhotoResponse(BaseModel):
    id: int
    object_key: str
    thumb_key: str | None
    original_filename: str | None
    width: int | None
    height: int | None
    content_type: str | None
    created_at: dt.datetime

    model_config = {"from_attributes": True}


class EntryResponse(BaseModel):
    id: int
    text: str | None
    entry_date: dt.date
    photos: list[PhotoResponse]
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = {"from_attributes": True}
