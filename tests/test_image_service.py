import os
from io import BytesIO

from PIL import Image

from app.core import config as config_module
from app.core.config import get_settings
from app.services.image_service import generate_thumbnail


def _make_test_image_bytes(width: int = 800, height: int = 600) -> bytes:
    image = Image.new("RGB", (width, height), color="red")
    buf = BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


def test_generate_thumbnail_with_preset_maintains_aspect_ratio(tmp_path, monkeypatch):
    # Configure storage directory for this test run
    monkeypatch.setenv("THUMBNAIL_SERVICE_BASE_STORAGE_DIR", str(tmp_path))
    config_module.get_settings.cache_clear()
    settings = get_settings()

    original_bytes = _make_test_image_bytes(800, 600)
    metadata = generate_thumbnail(
        original_bytes,
        original_filename="test.jpg",
        preset="small",
        settings=settings,
    )

    assert metadata.width <= settings.presets["small"][0]
    assert metadata.height <= settings.presets["small"][1]
    # Aspect ratio ~ 4:3
    assert abs((metadata.width / metadata.height) - (4 / 3)) < 0.05


def test_generate_thumbnail_with_custom_size_respects_bounds(tmp_path, monkeypatch):
    monkeypatch.setenv("THUMBNAIL_SERVICE_BASE_STORAGE_DIR", str(tmp_path))
    config_module.get_settings.cache_clear()
    settings = get_settings()

    original_bytes = _make_test_image_bytes(2000, 1000)
    custom_width, custom_height = 500, 500

    metadata = generate_thumbnail(
        original_bytes,
        original_filename="test.jpg",
        custom_width=custom_width,
        custom_height=custom_height,
        settings=settings,
    )

    assert metadata.width <= custom_width
    assert metadata.height <= custom_height
    assert metadata.size_bytes > 0

