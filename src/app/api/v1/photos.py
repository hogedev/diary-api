from fastapi import APIRouter, Query
from fastapi.responses import Response

from ..deps import EntryServiceDep

router = APIRouter()


@router.get("/{photo_id}/image")
async def get_photo_image(
    photo_id: int,
    service: EntryServiceDep,
    w: int | None = Query(default=None, description="サムネイル取得時に指定"),
) -> Response:
    thumb = w is not None and w <= 800
    data, content_type = await service.get_photo_data(photo_id, thumb=thumb)
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


@router.delete("/{photo_id}", status_code=204)
async def delete_photo(photo_id: int, service: EntryServiceDep) -> None:
    await service.delete_photo(photo_id)
