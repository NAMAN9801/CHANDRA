"""
Project CHANDRA - Flask Backend Server
Full-featured API for PSR Analysis with configurable parameters
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import io
import uuid
import base64
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from scipy import ndimage
from skimage import feature
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

class ConfigurablePSRAnalyzer:
    """PSR Analyzer with configurable parameters"""
    
    def __init__(self, params=None):
        self.params = params or self.get_default_params()
    
    @staticmethod
    def get_default_params():
        return {
            'clahe_clip_limit': 2.0,
            'clahe_tile_size': 8,
            'basic_threshold': 50,
            'adaptive_block_size': 11,
            'adaptive_c': 2,
            'edge_sigma': 1.0,
            'peak_min_distance': 20,
            'roughness_size': 5
        }
    
    def enhance_image(self, image):
        """CLAHE enhancement with configurable parameters"""
        clip_limit = float(self.params.get('clahe_clip_limit', 2.0))
        tile_size = int(self.params.get('clahe_tile_size', 8))
        
        clahe = cv2.createCLAHE(
            clipLimit=clip_limit, 
            tileGridSize=(tile_size, tile_size)
        )
        return clahe.apply(image)
    
    def detect_psr(self, image):
        """PSR detection with configurable thresholds"""
        results = {}
        
        # Basic thresholding
        thresh_val = int(self.params.get('basic_threshold', 50))
        _, thresh = cv2.threshold(image, thresh_val, 255, cv2.THRESH_BINARY_INV)
        results['threshold'] = thresh
        
        # Adaptive thresholding
        block_size = int(self.params.get('adaptive_block_size', 11))
        if block_size % 2 == 0:
            block_size += 1  # Must be odd
        c_val = int(self.params.get('adaptive_c', 2))
        
        adaptive = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, block_size, c_val
        )
        results['adaptive'] = adaptive
        
        # Edge detection
        sigma = float(self.params.get('edge_sigma', 1.0))
        edges = feature.canny(image, sigma=sigma)
        results['edges'] = (edges.astype(np.uint8) * 255)
        
        return results
    
    def analyze_terrain(self, image):
        """Terrain analysis with configurable parameters"""
        min_dist = int(self.params.get('peak_min_distance', 20))
        roughness_size = int(self.params.get('roughness_size', 5))
        
        peaks = feature.peak_local_max(image, min_distance=min_dist)
        valleys = feature.peak_local_max(255 - image, min_distance=min_dist)
        roughness = ndimage.generic_filter(
            image.astype(np.float64), np.std, size=roughness_size
        )
        
        return {
            'peaks': peaks,
            'valleys': valleys,
            'roughness': roughness,
            'peak_count': len(peaks),
            'valley_count': len(valleys)
        }
    
    def calculate_statistics(self, image, psr_masks):
        """Calculate image and PSR statistics"""
        return {
            'image_stats': {
                'mean': float(np.mean(image)),
                'std': float(np.std(image)),
                'min': int(np.min(image)),
                'max': int(np.max(image)),
                'dynamic_range': int(np.ptp(image))
            },
            'psr_coverage': {
                method: float(np.sum(mask > 0) / mask.size * 100)
                for method, mask in psr_masks.items()
            }
        }
    
    def create_single_visualization(self, image, vis_type, psr_results=None, terrain=None):
        """Create individual visualization images"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        if vis_type == 'original':
            ax.imshow(image, cmap='gray')
            ax.set_title('Original Image', fontsize=14, color='white')
        elif vis_type == 'enhanced':
            enhanced = self.enhance_image(image)
            ax.imshow(enhanced, cmap='gray')
            ax.set_title('Enhanced Image (CLAHE)', fontsize=14, color='white')
        elif vis_type == 'threshold' and psr_results:
            ax.imshow(psr_results['threshold'], cmap='hot')
            ax.set_title('Basic Threshold PSR', fontsize=14, color='white')
        elif vis_type == 'adaptive' and psr_results:
            ax.imshow(psr_results['adaptive'], cmap='hot')
            ax.set_title('Adaptive Threshold PSR', fontsize=14, color='white')
        elif vis_type == 'edges' and psr_results:
            ax.imshow(psr_results['edges'], cmap='gray')
            ax.set_title('Edge Detection', fontsize=14, color='white')
        elif vis_type == 'roughness' and terrain:
            im = ax.imshow(terrain['roughness'], cmap='viridis')
            ax.set_title('Surface Roughness', fontsize=14, color='white')
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        
        ax.axis('off')
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#1a1a2e')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#1a1a2e', 
                    edgecolor='none', bbox_inches='tight', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    def full_analysis(self, image):
        """Run complete analysis pipeline"""
        enhanced = self.enhance_image(image)
        psr_results = self.detect_psr(enhanced)
        terrain = self.analyze_terrain(enhanced)
        stats = self.calculate_statistics(enhanced, psr_results)
        
        # Generate all visualizations
        visualizations = {
            'original': self.create_single_visualization(image, 'original'),
            'enhanced': self.create_single_visualization(image, 'enhanced'),
            'threshold': self.create_single_visualization(image, 'threshold', psr_results),
            'adaptive': self.create_single_visualization(image, 'adaptive', psr_results),
            'edges': self.create_single_visualization(image, 'edges', psr_results),
            'roughness': self.create_single_visualization(image, 'roughness', terrain=terrain)
        }
        
        # Add terrain stats
        stats['terrain'] = {
            'peak_count': terrain['peak_count'],
            'valley_count': terrain['valley_count'],
            'mean_roughness': float(np.mean(terrain['roughness']))
        }
        
        return {
            'visualizations': visualizations,
            'statistics': stats,
            'parameters': self.params
        }


# Store uploaded images temporarily
image_store = {}


@app.route('/')
def index():
    """Serve the main application"""
    return send_from_directory('static', 'index.html')


@app.route('/api/defaults', methods=['GET'])
def get_defaults():
    """Get default parameter values"""
    return jsonify(ConfigurablePSRAnalyzer.get_default_params())


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload an image for analysis"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read and validate image
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if image is None:
            return jsonify({'error': 'Invalid image file'}), 400
        
        # Generate unique ID
        image_id = str(uuid.uuid4())
        
        # Store image
        image_store[image_id] = image
        
        # Save to disk as backup
        filepath = os.path.join(UPLOAD_FOLDER, f"{image_id}.png")
        cv2.imwrite(filepath, image)
        
        # Create preview
        _, buffer = cv2.imencode('.png', image)
        preview = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'image_id': image_id,
            'preview': preview,
            'width': image.shape[1],
            'height': image.shape[0]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """Analyze uploaded image with given parameters"""
    data = request.get_json()
    
    if not data or 'image_id' not in data:
        return jsonify({'error': 'Image ID required'}), 400
    
    image_id = data['image_id']
    params = data.get('parameters', {})
    
    # Get image from store or disk
    if image_id in image_store:
        image = image_store[image_id]
    else:
        filepath = os.path.join(UPLOAD_FOLDER, f"{image_id}.png")
        if not os.path.exists(filepath):
            return jsonify({'error': 'Image not found'}), 404
        image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    
    try:
        analyzer = ConfigurablePSRAnalyzer(params)
        results = analyzer.full_analysis(image)
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview/<vis_type>', methods=['POST'])
def preview_single(vis_type):
    """Generate single visualization preview for real-time updates"""
    data = request.get_json()
    
    if not data or 'image_id' not in data:
        return jsonify({'error': 'Image ID required'}), 400
    
    image_id = data['image_id']
    params = data.get('parameters', {})
    
    # Get image
    if image_id in image_store:
        image = image_store[image_id]
    else:
        filepath = os.path.join(UPLOAD_FOLDER, f"{image_id}.png")
        if not os.path.exists(filepath):
            return jsonify({'error': 'Image not found'}), 404
        image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    
    try:
        analyzer = ConfigurablePSRAnalyzer(params)
        enhanced = analyzer.enhance_image(image)
        psr_results = analyzer.detect_psr(enhanced)
        terrain = analyzer.analyze_terrain(enhanced)
        
        vis = analyzer.create_single_visualization(
            image, vis_type, psr_results, terrain
        )
        
        # Also return relevant stats
        stats = analyzer.calculate_statistics(enhanced, psr_results)
        
        return jsonify({
            'visualization': vis,
            'statistics': stats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['POST'])
def export_results():
    """Export full analysis results as downloadable files"""
    data = request.get_json()
    
    if not data or 'image_id' not in data:
        return jsonify({'error': 'Image ID required'}), 400
    
    image_id = data['image_id']
    params = data.get('parameters', {})
    
    # Get image
    if image_id in image_store:
        image = image_store[image_id]
    else:
        filepath = os.path.join(UPLOAD_FOLDER, f"{image_id}.png")
        if not os.path.exists(filepath):
            return jsonify({'error': 'Image not found'}), 404
        image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    
    try:
        analyzer = ConfigurablePSRAnalyzer(params)
        
        # Create comprehensive visualization
        enhanced = analyzer.enhance_image(image)
        psr_results = analyzer.detect_psr(enhanced)
        terrain = analyzer.analyze_terrain(enhanced)
        stats = analyzer.calculate_statistics(enhanced, psr_results)
        
        # Create 6-panel figure
        fig = plt.figure(figsize=(18, 12))
        fig.patch.set_facecolor('#1a1a2e')
        
        plots = [
            (231, image, 'gray', 'Original Image'),
            (232, enhanced, 'gray', 'Enhanced (CLAHE)'),
            (233, psr_results['threshold'], 'hot', 'Basic Threshold PSR'),
            (234, psr_results['adaptive'], 'hot', 'Adaptive Threshold PSR'),
            (235, psr_results['edges'], 'gray', 'Edge Detection'),
            (236, terrain['roughness'], 'viridis', 'Surface Roughness')
        ]
        
        for pos, data, cmap, title in plots:
            ax = plt.subplot(pos)
            ax.imshow(data, cmap=cmap)
            ax.set_title(title, fontsize=12, color='white', pad=10)
            ax.axis('off')
            ax.set_facecolor('#1a1a2e')
        
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#1a1a2e', 
                    edgecolor='none', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        export_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return jsonify({
            'export_image': export_b64,
            'statistics': stats,
            'parameters': params,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'CHANDRA PSR Analyzer'})


if __name__ == '__main__':
    print("=" * 50)
    print("  Project CHANDRA - PSR Analysis Server")
    print("=" * 50)
    print(f"  Starting server at http://localhost:5000")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
