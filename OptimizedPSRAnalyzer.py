import cv2
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json
from scipy import ndimage
from skimage import feature
import sys

class OptimizedPSRAnalyzer:
    def __init__(self, output_dir=None):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = output_dir or f"psr_analysis_{self.timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)

    def print_progress(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def load_sample_image(self, image_source):
        """Load image from local file path or URL"""
        self.print_progress(f"Loading image from: {image_source}")
        try:
            # Check if it's a URL or local file path
            if image_source.startswith(('http://', 'https://')):
                # Download image from URL
                response = requests.get(image_source)
                response.raise_for_status()
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
            else:
                # Load from local file
                if not os.path.exists(image_source):
                    raise FileNotFoundError(f"Image file not found: {image_source}")
                image = cv2.imread(image_source, cv2.IMREAD_GRAYSCALE)
            
            if image is None:
                raise ValueError("Failed to decode image")
            return image
        except Exception as e:
            self.print_progress(f"Error loading image: {str(e)}")
            return None

    def enhance_image(self, image):
        """Clahe for image enhancement"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(image)
        return enhanced

    def detect_psr_multi(self, image):
        """Multiple PSR detection methods"""
        results = {}
        
        # 1. Basic thresholding
        _, thresh = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY_INV)
        results['threshold'] = thresh
        
        # 2. Adaptive thresholding
        adaptive = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        results['adaptive'] = adaptive
        
        # 3. Edge detection
        edges = feature.canny(image, sigma=1)
        results['edges'] = edges.astype(np.uint8) * 255
        
        return results

    def analyze_terrain(self, image):
        """Analyze terrain features"""
        # Peaks and valleys
        peaks = feature.peak_local_max(image, min_distance=20)
        valleys = feature.peak_local_max(-image, min_distance=20)
        
        # Roughness (local standard deviation)
        roughness = ndimage.generic_filter(image, np.std, size=5)
        
        return {
            'peaks': peaks,
            'valleys': valleys,
            'roughness': roughness
        }

    def calculate_statistics(self, image, psr_masks):
        """Stats of the image"""
        stats = {
            'image_stats': {
                'mean': np.mean(image),
                'std': np.std(image),
                'min': np.min(image),
                'max': np.max(image),
                'dynamic_range': np.ptp(image)
            },
            'psr_coverage': {
                method: (np.sum(mask > 0) / mask.size * 100)
                for method, mask in psr_masks.items()
            }
        }
        return stats

    def save_results(self, stats, output_path):
        serializable_stats = {
            'image_stats': {k: float(v) for k, v in stats['image_stats'].items()},
            'psr_coverage': {k: float(v) for k, v in stats['psr_coverage'].items()},
            'landing_assessment': stats.get('landing_assessment', {})
        }
        with open(os.path.join(output_path, 'statistics.json'), 'w', encoding='utf-8') as file_obj:
            json.dump(serializable_stats, file_obj, indent=2)

    def create_visualization(self, image, psr_results, terrain_analysis, stats):
        """Main visualization of the program"""
        fig = plt.figure(figsize=(15, 12))  # Increased height to accommodate text
        plt.subplots_adjust(hspace=0.4)  # Increase vertical space between subplots
        
        # Original and enhanced image
        ax1 = plt.subplot(231)
        ax1.imshow(image, cmap='gray')
        ax1.set_title('Original Image')
        
        # PSR detection methods
        ax2 = plt.subplot(232)
        ax2.imshow(psr_results['threshold'], cmap='hot')
        ax2.set_title('Basic Threshold PSR')
        
        ax3 = plt.subplot(233)
        ax3.imshow(psr_results['adaptive'], cmap='hot')
        ax3.set_title('Adaptive Threshold PSR')
        
        # Terrain analysis
        ax4 = plt.subplot(234)
        ax4.imshow(terrain_analysis['roughness'], cmap='viridis')
        ax4.set_title('Surface Roughness')
        
        # Edge detection
        ax5 = plt.subplot(235)
        ax5.imshow(psr_results['edges'], cmap='gray')
        ax5.set_title('Edge Detection')
        
        # Statistics text
        ax6 = plt.subplot(236)
        ax6.axis('off')
        stats_text = (
            f"PSR Coverage:\n"
            f"Basic: {stats['psr_coverage']['threshold']:.1f}%\n"
            f"Adaptive: {stats['psr_coverage']['adaptive']:.1f}%\n"
            f"\nImage Statistics:\n"
            f"Mean: {stats['image_stats']['mean']:.1f}\n"
            f"Std: {stats['image_stats']['std']:.1f}\n"
            f"Dynamic Range: {stats['image_stats']['dynamic_range']}"
        )
        ax6.text(0.1, 0.5, stats_text, fontsize=10)
        
        plt.tight_layout()
        return fig

    def analyze_and_visualize(self, image_path):
        """Run full image analysis pipeline for a local file path."""
        image = self.load_local_image(image_path)
        if image is None:
            return None

        self.print_progress("Enhancing image...")
        enhanced = self.enhance_image(image)

        self.print_progress("Detecting PSR regions...")
        psr_results = self.detect_psr_multi(enhanced)

        self.print_progress("Analyzing terrain...")
        terrain_analysis = self.analyze_terrain(enhanced)

        self.print_progress("Calculating statistics...")
        stats = self.calculate_statistics(enhanced, psr_results)

        self.print_progress("Saving results...")
        self.save_results(stats, self.output_dir)

        self.print_progress("Creating visualization...")
        fig = self.create_visualization(image, psr_results, terrain_analysis, stats)
        
        # Save figure locally
        output_path = os.path.join(self.output_dir, 'analysis_result.png')
        plt.savefig(output_path)
        plt.close()

        return {
            'output_image_path': output_path,
            'stats': {
                'image_stats': {k: float(v) for k, v in stats['image_stats'].items()},
                'psr_coverage': {k: float(v) for k, v in stats['psr_coverage'].items()}
            },
            'landing_assessment': stats['landing_assessment']
        }


def run_analysis(image_path, output_dir=None):
    """Function-level API for programmatic use.

    Returns structured metadata for API clients.
    """
    analyzer = OptimizedPSRAnalyzer(output_dir=output_dir)
    result = analyzer.analyze_and_visualize(image_path)

    if result is None:
        raise ValueError("Analysis failed for image path")

    return result

def main():
    analyzer = OptimizedPSRAnalyzer()
    
    # Specify your image path here
    image_path = "image copy.png"
    
    # Run analysis and get result path
    result_path = analyzer.analyze_and_visualize(image_path)
    if result_path:
        print(f"Analysis complete! Result image saved at: {result_path}")
    else:
        print("Analysis failed!")

if __name__ == "__main__":
    main()
