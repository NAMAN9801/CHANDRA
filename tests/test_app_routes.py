import io
from types import SimpleNamespace


def test_upload_missing_file_returns_400(client):
    response = client.post("/upload", data={}, content_type="multipart/form-data")

    assert response.status_code == 400
    assert response.get_json() == {"error": "No file part"}


def test_upload_empty_filename_returns_400(client):
    response = client.post(
        "/upload",
        data={"image": (io.BytesIO(b"abc"), "")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "No selected file"}


def test_upload_invalid_image_returns_400(client):
    response = client.post(
        "/upload",
        data={"image": (io.BytesIO(b"not-an-image"), "bad.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid image file"}


def test_upload_valid_image_returns_display_contract(client, small_png_bytes):
    response = client.post(
        "/upload",
        data={"image": (small_png_bytes, "tiny.png")},
        content_type="multipart/form-data",
    )

    body = response.get_json()
    assert response.status_code == 200
    assert set(body) == {"original_path", "display_url"}
    assert body["original_path"].endswith(".png")
    assert "/display/" in body["display_url"]


def test_analyze_missing_payload_returns_400(client):
    response = client.post("/analyze", json={})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Display URL is required"}


def test_analyze_missing_image_returns_404(client):
    response = client.post(
        "/analyze", json={"display_url": "http://localhost/display/does-not-exist.png"}
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Image not found"}


def test_analyze_happy_path_returns_result(client, small_png_bytes, monkeypatch):
    upload_response = client.post(
        "/upload",
        data={"image": (small_png_bytes, "tiny.png")},
        content_type="multipart/form-data",
    )
    display_url = upload_response.get_json()["display_url"]

    def _fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="analysis-ok", stderr="")

    monkeypatch.setattr("subprocess.run", _fake_run)

    response = client.post("/analyze", json={"display_url": display_url})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload == {"success": True, "analysis_result": "analysis-ok"}


def test_analyze_subprocess_error_returns_500(client, small_png_bytes, monkeypatch):
    upload_response = client.post(
        "/upload",
        data={"image": (small_png_bytes, "tiny.png")},
        content_type="multipart/form-data",
    )
    display_url = upload_response.get_json()["display_url"]

    def _fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="boom")

    monkeypatch.setattr("subprocess.run", _fake_run)

    response = client.post("/analyze", json={"display_url": display_url})

    assert response.status_code == 500
    assert response.get_json() == {"error": "Analysis failed: boom"}
