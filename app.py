from flask import Flask, request, jsonify, send_file

from services.analysis_service import (
    AnalysisExecutionError,
    AnalysisService,
    RequestValidationError,
)
from services.storage import (
    ImageNotFoundError,
    InvalidImageError,
    StorageError,
    StorageRepository,
)

app = Flask(__name__)
storage = StorageRepository()
analysis_service = AnalysisService(storage=storage)


@app.route('/upload', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file_obj = request.files['image']
    if file_obj.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        host_url = request.host_url.rstrip('/')
        response = analysis_service.handle_upload(file_obj=file_obj, host_url=host_url)
        return jsonify(response.to_dict())
    except InvalidImageError as exc:
        return jsonify({'error': str(exc)}), 400
    except StorageError as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/display/<request_id>', methods=['GET'])
def display_image(request_id):
    try:
        filepath = storage.get_uploaded_image(request_id)
        return send_file(filepath, mimetype='image/png', as_attachment=False)
    except ImageNotFoundError as exc:
        return jsonify({'error': str(exc)}), 404
    except StorageError as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/analyze', methods=['POST'])
def analyze_image():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({'error': 'Display URL is required'}), 400

    try:
        response = analysis_service.analyze(payload)
        return jsonify(response.to_dict())
    except RequestValidationError as exc:
        return jsonify({'error': str(exc)}), 400
    except ImageNotFoundError as exc:
        return jsonify({'error': str(exc)}), 404
    except AnalysisExecutionError as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/', methods=['GET'])
def index():
    return 'Image Upload and Analysis Service is running.'


if __name__ == '__main__':
    app.run(debug=True)
