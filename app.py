import os
import subprocess
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from PIL import Image


def create_app() -> Flask:
    app = Flask(__name__)

    flask_env = os.getenv("FLASK_ENV", "production")
    output_dir = os.getenv("OUTPUT_DIR", "uploads")
    max_content_length_mb = int(os.getenv("MAX_CONTENT_LENGTH_MB", "16"))
    cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*")

    app.config["ENV"] = flask_env
    app.config["UPLOAD_FOLDER"] = output_dir
    app.config["MAX_CONTENT_LENGTH"] = max_content_length_mb * 1024 * 1024

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if not allowed_origins or "*" in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
        elif origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin

        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return response

    def save_uploaded_file(file) -> str:
        """Save uploaded file to disk and return the file path."""
        filename = f"{uuid.uuid4()}.png"
        filepath = Path(app.config["UPLOAD_FOLDER"]) / filename

        img = Image.open(file)
        img.save(filepath)

        return str(filepath)

    @app.route("/health", methods=["GET"])
    def health() -> tuple:
        return jsonify({"status": "ok", "env": app.config["ENV"]}), 200

    @app.route("/upload", methods=["POST"])
    def process_image() -> tuple:
        try:
            if "image" not in request.files:
                return jsonify({"error": "No file part"}), 400

            file = request.files["image"]
            if file.filename == "":
                return jsonify({"error": "No selected file"}), 400

            try:
                Image.open(file).verify()
                file.seek(0)
            except Exception:
                return jsonify({"error": "Invalid image file"}), 400

            filepath = save_uploaded_file(file)
            host_url = request.host_url.rstrip("/")

            result_data = {
                "original_path": filepath,
                "display_url": f"{host_url}/display/{Path(filepath).name}",
            }
            return jsonify(result_data), 200

        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/display/<filename>", methods=["GET"])
    def display_image(filename: str):
        try:
            filepath = Path(app.config["UPLOAD_FOLDER"]) / filename

            if not filepath.exists():
                return jsonify({"error": "Image not found"}), 404

            return send_file(filepath, mimetype="image/png", as_attachment=False)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/analyze", methods=["POST"])
    def analyze_image() -> tuple:
        try:
            data = request.get_json()
            if not data or "display_url" not in data:
                return jsonify({"error": "Display URL is required"}), 400

            display_url = data["display_url"]
            filename = display_url.split("/")[-1]
            filepath = Path(app.config["UPLOAD_FOLDER"]) / filename

            if not filepath.exists():
                return jsonify({"error": "Image not found"}), 404

            script_path = Path(__file__).resolve().parent / "OptimizedPSRAnalyzer.py"

            result = subprocess.run(
                ["python", str(script_path), str(filepath)],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                return jsonify({"error": f"Analysis failed: {result.stderr}"}), 500

            return jsonify({"success": True, "analysis_result": result.stdout}), 200

        except subprocess.SubprocessError as exc:
            return jsonify({"error": f"Failed to run analysis: {str(exc)}"}), 500
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/", methods=["GET"])
    def index() -> str:
        return "Image Upload and Analysis Service is running."

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host=host, port=port, debug=app.config["ENV"] == "development")
