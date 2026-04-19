import datetime as dt
import io
import uuid

from PIL import Image

from ..config import settings
from ..models.photo import Photo


def process_upload(
    data: bytes,
    filename: str | None,
    content_type: str | None,
    entry_date: dt.date,
) -> tuple[Photo, bytes, bytes | None]:
    """写真データを処理し、Photo モデルとオリジナル/サムネイルバイトを返す。"""
    img = Image.open(io.BytesIO(data))
    width, height = img.size

    ext = _detect_ext(content_type, filename)
    uid = uuid.uuid4().hex
    date_prefix = entry_date.strftime("%Y/%m/%d")
    object_key = f"{date_prefix}/{uid}.{ext}"

    # サムネイル生成
    thumb_key: str | None = None
    thumb_bytes: bytes | None = None
    max_dim = settings.thumb_max_dimension
    if max(width, height) > max_dim:
        thumb_key = f"{date_prefix}/{uid}_thumb.jpg"
        thumb_img = img.copy()
        thumb_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        if thumb_img.mode in ("RGBA", "P"):
            thumb_img = thumb_img.convert("RGB")
        buf = io.BytesIO()
        thumb_img.save(buf, format="JPEG", quality=85)
        thumb_bytes = buf.getvalue()

    photo = Photo(
        object_key=object_key,
        thumb_key=thumb_key,
        original_filename=filename,
        width=width,
        height=height,
        size_bytes=len(data),
        content_type=content_type or "image/jpeg",
    )
    return photo, data, thumb_bytes


def _detect_ext(content_type: str | None, filename: str | None) -> str:
    if filename and "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    mapping = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "image/gif": "gif",
        "image/heic": "heic",
    }
    return mapping.get(content_type or "", "jpg")
