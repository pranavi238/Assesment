from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.core import config as config_module
from app.core.config import get_settings
from app.main import create_app


def _make_test_image_bytes(width: int = 800, height: int = 600) -> bytes:
    image = Image.new("RGB", (width, height), color="blue")
    buf = BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


def _create_test_client(tmp_path) -> TestClient:
    # Ensure settings use a temporary storage directory
    config_module.get_settings.cache_clear()
    config_module.Settings.base_storage_dir = tmp_path  # type: ignore[attr-defined]
    app = create_app()
    return TestClient(app)


def test_health_endpoint(tmp_path):
    client = _create_test_client(tmp_path)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_retrieve_thumbnail_with_preset(tmp_path):
    client = _create_test_client(tmp_path)

    image_bytes = _make_test_image_bytes()
    files = [("files", ("test.jpg", image_bytes, "image/jpeg"))]

    response = client.post("/thumbnails", files=files, data={"preset": "small"})
    assert response.status_code == 201

    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1

    thumb = body[0]
    assert "id" in thumb
    thumb_id = thumb["id"]

    get_response = client.get(f"/thumbnails/{thumb_id}")
    assert get_response.status_code == 200
    assert get_response.headers["content-type"].startswith("image/")


def test_create_thumbnails_with_invalid_preset_returns_400(tmp_path):
    client = _create_test_client(tmp_path)

    image_bytes = _make_test_image_bytes()
    files = [("files", ("test.jpg", image_bytes, "image/jpeg"))]

    response = client.post("/thumbnails", files=files, data={"preset": "unknown"})
    assert response.status_code == 400
    assert "Unknown preset" in response.json()["detail"]

