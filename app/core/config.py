from functools import lru_cache
from pathlib import Path
from typing import Dict, Tuple

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_storage_dir: Path = Field(default=Path("data"), description="Base directory for all image storage")
    uploads_dir_name: str = Field(default="uploads", description="Subdirectory for original uploads")
    thumbnails_dir_name: str = Field(default="thumbnails", description="Subdirectory for generated thumbnails")

    max_files_per_request: int = Field(default=10, ge=1, le=50)
    max_custom_size: int = Field(default=2048, ge=1)

    presets: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            "small": (128, 128),
            "medium": (256, 256),
            "large": (512, 512),
        }
    )

    allowed_formats: Tuple[str, ...] = ("JPEG", "PNG", "WEBP")

    class Config:
        env_prefix = "THUMBNAIL_SERVICE_"
        case_sensitive = False

    @property
    def uploads_path(self) -> Path:
        return self.base_storage_dir / self.uploads_dir_name

    @property
    def thumbnails_path(self) -> Path:
        return self.base_storage_dir / self.thumbnails_dir_name


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.base_storage_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_path.mkdir(parents=True, exist_ok=True)
    settings.thumbnails_path.mkdir(parents=True, exist_ok=True)
    return settings

