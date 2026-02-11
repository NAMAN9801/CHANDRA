import io
import unittest

from PIL import Image

from app import create_app


def png_bytes() -> io.BytesIO:
    payload = io.BytesIO()
    image = Image.new("RGB", (8, 8), color="black")
    image.save(payload, format="PNG")
    payload.seek(0)
    return payload


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_upload_rejects_missing_file(self):
        response = self.client.post("/upload", data={}, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_upload_accepts_png(self):
        data = {"image": (png_bytes(), "sample.png")}
        response = self.client.post("/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertIn("display_url", body)
        self.assertIn("original_path", body)


if __name__ == "__main__":
    unittest.main()
