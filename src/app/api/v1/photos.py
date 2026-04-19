from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from ...exceptions import AppError
from ...services.auth_service import decode_token
from ..deps import CurrentUserId, EntryServiceDep

router = APIRouter()


@router.get("/{photo_id}/image")
async def get_photo_image(
    photo_id: int,
    service: EntryServiceDep,
    token: str = Query(..., description="認証トークン"),  # noqa: B008
    w: int | None = Query(default=None, description="サムネイル取得時に指定"),  # noqa: B008
) -> Response:
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except AppError as err:
        raise HTTPException(status_code=401, detail="Invalid token") from err
    thumb = w is not None and w <= 800
    data, content_type = await service.get_photo_data(photo_id, user_id, thumb=thumb)
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


@router.delete("/{photo_id}", status_code=204)
async def delete_photo(photo_id: int, service: EntryServiceDep, user_id: CurrentUserId) -> None:
    await service.delete_photo(photo_id, user_id)
