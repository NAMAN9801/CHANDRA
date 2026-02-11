from flask import Flask, request, jsonify, send_file
import os
from PIL import Image, UnidentifiedImageError
import uuid

from OptimizedPSRAnalyzer import OptimizedPSRAnalyzer

app = Flask(__name__)

# Create a folder for storing uploaded images
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


analyzer = OptimizedPSRAnalyzer()


def save_uploaded_file(file):
    """Save uploaded file to disk and return the file path."""
    try:
        filename = str(uuid.uuid4()) + '.png'
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        img = Image.open(file)
        img.save(filepath)

        return filepath
    except Exception as e:
        raise Exception(f"File save failed: {str(e)}")


@app.route('/upload', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        try:
            Image.open(file).verify()
            file.seek(0)
        except UnidentifiedImageError:
            return jsonify({'error': 'Unsupported image format'}), 400
        except Exception:
            return jsonify({'error': 'Invalid image file'}), 400

        filepath = save_uploaded_file(file)

        host_url = request.host_url.rstrip('/')

        result_data = {
            'original_path': filepath,
            'display_url': f'{host_url}/display/{os.path.basename(filepath)}'
        }

        return jsonify(result_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/display/<filename>', methods=['GET'])
def display_image(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(filepath):
            return jsonify({'error': 'Image not found'}), 404

        return send_file(
            filepath,
            mimetype='image/png',
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        data = request.get_json()
        if not data or 'display_url' not in data:
            return jsonify({'error': 'Display URL is required'}), 400

        display_url = data['display_url']
        filename = display_url.split('/')[-1]
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(filepath):
            return jsonify({'error': 'Image not found'}), 404
        if not os.path.isfile(filepath):
            return jsonify({'error': 'Provided upload path is not a file'}), 400

        try:
            Image.open(filepath).verify()
        except UnidentifiedImageError:
            return jsonify({'error': 'Unsupported image format'}), 400
        except Exception:
            return jsonify({'error': 'Unreadable image file'}), 400

        try:
            output_path = analyzer.analyze_and_visualize(image_path=filepath)
        except (FileNotFoundError, ValueError) as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

        return jsonify({
            'success': True,
            'analysis_result_path': output_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    return "Image Upload and Analysis Service is running."


if __name__ == '__main__':
    app.run(debug=True)
