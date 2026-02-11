import io
import pathlib
import sys

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    monkeypatch.setattr(app_module, "UPLOAD_FOLDER", str(upload_dir))

    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def small_png_bytes():
    img = Image.fromarray(np.array([[0, 255], [128, 64]], dtype=np.uint8), mode="L")
    payload = io.BytesIO()
    img.save(payload, format="PNG")
    payload.seek(0)
    return payload
