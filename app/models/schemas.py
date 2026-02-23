from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ThumbnailMetadata(BaseModel):
    id: str = Field(..., description="Unique identifier for the thumbnail")
    original_filename: Optional[str] = Field(
        None, description="Original uploaded filename, if available"
    )
    preset: Optional[str] = Field(
        None, description="Preset name used for resizing (small, medium, large)"
    )
    custom_width: Optional[int] = Field(
        None, description="Requested custom width, if custom size was used"
    )
    custom_height: Optional[int] = Field(
        None, description="Requested custom height, if custom size was used"
    )
    width: int = Field(..., description="Actual thumbnail width in pixels")
    height: int = Field(..., description="Actual thumbnail height in pixels")
    content_type: str = Field(..., description="MIME type of the thumbnail image")
    size_bytes: int = Field(..., description="Size of the thumbnail on disk in bytes")
    url: str = Field(..., description="Relative URL to retrieve the thumbnail")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the thumbnail was created",
    )

