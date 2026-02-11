from types import SimpleNamespace


def test_upload_then_analyze_end_to_end_with_test_client(client, small_png_bytes, monkeypatch):
    upload_response = client.post(
        "/upload",
        data={"image": (small_png_bytes, "fixture.png")},
        content_type="multipart/form-data",
    )

    assert upload_response.status_code == 200
    upload_payload = upload_response.get_json()

    observed = {}

    def _fake_run(cmd, capture_output, text):
        observed["cmd"] = cmd
        observed["capture_output"] = capture_output
        observed["text"] = text
        return SimpleNamespace(returncode=0, stdout="fixture-analysis", stderr="")

    monkeypatch.setattr("subprocess.run", _fake_run)

    analyze_response = client.post("/analyze", json={"display_url": upload_payload["display_url"]})

    assert analyze_response.status_code == 200
    assert analyze_response.get_json() == {
        "success": True,
        "analysis_result": "fixture-analysis",
    }
    assert observed["capture_output"] is True
    assert observed["text"] is True
    assert observed["cmd"][0] == "python"
    assert observed["cmd"][2].endswith(".png")
