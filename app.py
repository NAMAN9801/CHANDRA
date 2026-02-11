from datetime import datetime, timedelta, timezone
import glob
import os
import subprocess
import uuid

from flask import Flask, jsonify, request, send_file
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
UPLOAD_TTL_SECONDS = int(os.getenv("UPLOAD_TTL_SECONDS", str(24 * 60 * 60)))

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_MB * 1024 * 1024

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
FORMAT_TO_EXTENSION = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}


class UploadValidationError(Exception):
    """Raised when uploaded image payload fails validation."""


def now_utc():
    return datetime.now(timezone.utc)


def cleanup_expired_uploads():
    cutoff_time = now_utc() - timedelta(seconds=UPLOAD_TTL_SECONDS)
    removed_count = 0

    for filepath in glob.glob(os.path.join(UPLOAD_FOLDER, "*.*")):
        try:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc)
            if file_mtime < cutoff_time:
                os.remove(filepath)
                removed_count += 1
        except OSError:
            continue

    return removed_count


def resolve_upload_path(image_id: str):
    matches = glob.glob(os.path.join(UPLOAD_FOLDER, f"{image_id}.*"))
    if not matches:
        return None
    return matches[0]


def iso_expiry_for(filepath: str):
    expires_at = datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc) + timedelta(seconds=UPLOAD_TTL_SECONDS)
    return expires_at.isoformat()


def save_uploaded_file(file):
    original_filename = secure_filename(file.filename or "")
    if not original_filename:
        raise UploadValidationError("Filename is invalid.")

    original_extension = os.path.splitext(original_filename)[1].lower()
    if original_extension not in ALLOWED_EXTENSIONS:
        raise UploadValidationError("Unsupported file extension.")

    try:
        image = Image.open(file.stream)
        image.verify()
        file.stream.seek(0)
        image = Image.open(file.stream)
    except (UnidentifiedImageError, OSError):
        raise UploadValidationError("Uploaded file is not a valid image.")

    image_format = (image.format or "").upper()
    if image_format not in FORMAT_TO_EXTENSION:
        raise UploadValidationError("Unsupported image format.")

    image_id = uuid.uuid4().hex
    normalized_extension = FORMAT_TO_EXTENSION[image_format]
    filename = f"{image_id}.{normalized_extension}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    image.save(filepath, format=image_format)

    return {
        "image_id": image_id,
        "filename": filename,
        "filepath": filepath,
        "format": image_format,
    }


def build_upload_response(upload):
    image_id = upload["image_id"]
    base_url = request.host_url.rstrip("/")
    filepath = upload["filepath"]

    return {
        "version": "v1",
        "data": {
            "image_id": image_id,
            "display_url": f"{base_url}/api/v1/uploads/{image_id}",
            "delete_url": f"{base_url}/api/v1/uploads/{image_id}",
            "expires_at": iso_expiry_for(filepath),
        },
    }


@app.before_request
def maintain_upload_retention():
    cleanup_expired_uploads()


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(_error):
    return jsonify({"version": "v1", "error": f"File too large. Max size is {MAX_UPLOAD_SIZE_MB}MB."}), 413


@app.route("/api/v1/uploads", methods=["POST"])
def upload_image_v1():
    if "image" not in request.files:
        return jsonify({"version": "v1", "error": "No file part."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"version": "v1", "error": "No selected file."}), 400

    try:
        upload = save_uploaded_file(file)
        return jsonify(build_upload_response(upload)), 201
    except UploadValidationError as error:
        return jsonify({"version": "v1", "error": str(error)}), 400
    except Exception as error:
        return jsonify({"version": "v1", "error": f"Upload failed: {str(error)}"}), 500


@app.route("/api/v1/uploads/<image_id>", methods=["GET"])
def display_image_v1(image_id):
    filepath = resolve_upload_path(image_id)
    if not filepath:
        return jsonify({"version": "v1", "error": "Image not found."}), 404

    extension = os.path.splitext(filepath)[1].lower()
    mimetype_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    mimetype = mimetype_map.get(extension, "application/octet-stream")

    return send_file(filepath, mimetype=mimetype, as_attachment=False)


@app.route("/api/v1/uploads/<image_id>", methods=["DELETE"])
def delete_upload_v1(image_id):
    filepath = resolve_upload_path(image_id)
    if not filepath:
        return jsonify({"version": "v1", "error": "Image not found."}), 404

    try:
        os.remove(filepath)
    except OSError as error:
        return jsonify({"version": "v1", "error": f"Failed to delete image: {str(error)}"}), 500

    return jsonify({"version": "v1", "data": {"deleted": True, "image_id": image_id}})


@app.route("/api/v1/analyze", methods=["POST"])
def analyze_image_v1():
    data = request.get_json(silent=True) or {}
    image_id = data.get("image_id")

    if not image_id:
        return jsonify({"version": "v1", "error": "image_id is required."}), 400

    filepath = resolve_upload_path(image_id)
    if not filepath:
        return jsonify({"version": "v1", "error": "Image not found."}), 404

    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "OptimizedPSRAnalyzer.py")

    try:
        result = subprocess.run(["python", script_path, filepath], capture_output=True, text=True)
    except subprocess.SubprocessError as error:
        return jsonify({"version": "v1", "error": f"Failed to run analysis: {str(error)}"}), 500

    if result.returncode != 0:
        return jsonify({"version": "v1", "error": f"Analysis failed: {result.stderr}"}), 500

    return jsonify({"version": "v1", "data": {"image_id": image_id, "analysis_result": result.stdout}})


# Backward-compatible aliases
@app.route("/upload", methods=["POST"])
def upload_image_legacy():
    return upload_image_v1()


@app.route("/display/<image_id>", methods=["GET"])
def display_image_legacy(image_id):
    return display_image_v1(image_id)


@app.route("/analyze", methods=["POST"])
def analyze_image_legacy():
    return analyze_image_v1()


@app.route("/", methods=["GET"])
def index():
    return "Image Upload and Analysis Service is running."


if __name__ == "__main__":
    app.run(debug=True)
