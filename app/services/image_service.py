from io import BytesIO
from typing import Optional, Tuple
from uuid import uuid4

from PIL import Image

from app.core.config import Settings, get_settings
from app.models.schemas import ThumbnailMetadata
from app.services.storage_service import build_thumbnail_url, get_thumbnail_path


class UnsupportedImageFormatError(ValueError):
    pass


def _get_target_dimensions(
    image_size: Tuple[int, int], max_width: int, max_height: int
) -> Tuple[int, int]:
    """
    Compute target dimensions preserving aspect ratio, fitting within a bounding box.
    """
    original_width, original_height = image_size
    ratio = min(max_width / original_width, max_height / original_height, 1.0)
    target_width = int(original_width * ratio)
    target_height = int(original_height * ratio)
    return max(target_width, 1), max(target_height, 1)


def generate_thumbnail(
    image_bytes: bytes,
    *,
    original_filename: Optional[str] = None,
    preset: Optional[str] = None,
    custom_width: Optional[int] = None,
    custom_height: Optional[int] = None,
    settings: Optional[Settings] = None,
) -> ThumbnailMetadata:
    """
    Generate a thumbnail from raw image bytes and return its metadata.
    """
    settings = settings or get_settings()

    with Image.open(BytesIO(image_bytes)) as image:
        if image.format not in settings.allowed_formats:
            raise UnsupportedImageFormatError(
                f"Unsupported image format: {image.format}"
            )

        if preset:
            try:
                max_width, max_height = settings.presets[preset]
            except KeyError as exc:
                raise ValueError(f"Unknown preset: {preset}") from exc
        else:
            if not (custom_width and custom_height):
                raise ValueError("Both custom_width and custom_height must be provided")
            if (
                custom_width > settings.max_custom_size
                or custom_height > settings.max_custom_size
            ):
                raise ValueError("Requested size exceeds maximum allowed dimensions")
            max_width, max_height = custom_width, custom_height

        target_width, target_height = _get_target_dimensions(
            image.size, max_width, max_height
        )

        image = image.convert("RGB")
        image.thumbnail((target_width, target_height))

        thumbnail_id = uuid4().hex
        thumbnail_path = get_thumbnail_path(thumbnail_id)
        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(thumbnail_path, format="JPEG")

        size_bytes = thumbnail_path.stat().st_size
        content_type = "image/jpeg"

        return ThumbnailMetadata(
            id=thumbnail_id,
            original_filename=original_filename,
            preset=preset,
            custom_width=custom_width,
            custom_height=custom_height,
            width=image.width,
            height=image.height,
            content_type=content_type,
            size_bytes=size_bytes,
            url=build_thumbnail_url(thumbnail_id),
        )

