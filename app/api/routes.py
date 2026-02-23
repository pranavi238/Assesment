from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.models.schemas import ThumbnailMetadata
from app.services.image_service import (
    UnsupportedImageFormatError,
    generate_thumbnail,
)
from app.services.storage_service import get_thumbnail_path, thumbnail_exists

router = APIRouter()


@router.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


@router.post(
    "/thumbnails",
    response_model=List[ThumbnailMetadata],
    status_code=status.HTTP_201_CREATED,
    tags=["thumbnails"],
)
async def create_thumbnails(
    files: List[UploadFile] = File(..., description="One or more image files"),
    preset: Optional[str] = Form(
        default=None, description="Preset size: small, medium, or large"
    ),
    width: Optional[int] = Form(
        default=None, description="Custom maximum width (used with height)"
    ),
    height: Optional[int] = Form(
        default=None, description="Custom maximum height (used with width)"
    ),
) -> List[ThumbnailMetadata]:
    """
    Accept one or more images, generate thumbnails using either a preset
    or custom dimensions, and return metadata for each generated thumbnail.
    """
    settings = get_settings()

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one image file must be provided",
        )

    if len(files) > settings.max_files_per_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many files. Maximum allowed is {settings.max_files_per_request}",
        )

    using_preset = preset is not None
    using_custom = width is not None or height is not None

    if using_preset and using_custom:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specify either a preset or custom width/height, not both",
        )

    if not using_preset and not (width and height):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a preset or both width and height must be provided",
        )

    if preset is not None and preset not in get_settings().presets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown preset: {preset}",
        )

    thumbnails: List[ThumbnailMetadata] = []

    for file in files:
        content = await file.read()
        try:
            metadata = generate_thumbnail(
                content,
                original_filename=file.filename,
                preset=preset,
                custom_width=width,
                custom_height=height,
            )
        except UnsupportedImageFormatError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        thumbnails.append(metadata)

    return thumbnails


@router.get(
    "/thumbnails/{thumbnail_id}",
    response_class=FileResponse,
    responses={404: {"description": "Thumbnail not found"}},
    tags=["thumbnails"],
)
async def get_thumbnail(thumbnail_id: str) -> FileResponse:
    """
    Retrieve a generated thumbnail image by its ID.
    """
    if not thumbnail_exists(thumbnail_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail not found",
        )

    path = get_thumbnail_path(thumbnail_id)
    return FileResponse(path, media_type="image/jpeg")

