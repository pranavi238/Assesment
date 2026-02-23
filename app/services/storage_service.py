from pathlib import Path

from app.core.config import get_settings


def get_thumbnail_path(thumbnail_id: str) -> Path:
    """
    Resolve the filesystem path for a stored thumbnail.
    """
    settings = get_settings()
    return settings.thumbnails_path / f"{thumbnail_id}.jpg"


def thumbnail_exists(thumbnail_id: str) -> bool:
    """
    Check whether a thumbnail with the given ID exists.
    """
    return get_thumbnail_path(thumbnail_id).is_file()


def build_thumbnail_url(thumbnail_id: str) -> str:
    """
    Build the relative URL for retrieving a thumbnail.
    """
    return f"/thumbnails/{thumbnail_id}"

