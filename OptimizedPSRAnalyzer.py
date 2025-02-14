import cv2
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import pandas as pd
from scipy import ndimage
from skimage import feature

class OptimizedPSRAnalyzer:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"psr_analysis_{self.timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)

    def print_progress(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def load_sample_image(self, path):
        self.print_progress(f"Loading image from: {path}")
        try:
            image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise ValueError("Failed to load image")
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
        pd.DataFrame(stats).to_csv(os.path.join(output_path, 'statistics.csv'))

    def create_visualization(self, image, psr_results, terrain_analysis, stats):
        """Main visualization of the program"""
        fig = plt.figure(figsize=(15, 10))
        
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
            f"Adaptive: {stats['psr_coverage']['adaptive']:.1f}%\n\n"
            f"Image Statistics:\n"
            f"Mean: {stats['image_stats']['mean']:.1f}\n"
            f"Std: {stats['image_stats']['std']:.1f}\n"
            f"Dynamic Range: {stats['image_stats']['dynamic_range']}"
        )
        ax6.text(0.1, 0.5, stats_text, fontsize=10)
        
        plt.tight_layout()
        return fig

    def analyze_and_visualize(self, image_path):
        """Main analysis function"""
        # Load image
        image = self.load_sample_image(image_path)
        if image is None:
            return False

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
        
        # Save and show results
        output_path = os.path.join(self.output_dir, 'psr_analysis.png')
        plt.savefig(output_path)
        
        self.print_progress(f"Analysis complete! Results saved to: {self.output_dir}")
        plt.show()
        return True

def main():
    analyzer = OptimizedPSRAnalyzer()
    
    
    image_path = r'C:\Users\dhing\Desktop\Lunar PSR images\proto.PNG'
    
    # Run analysis
    analyzer.analyze_and_visualize(image_path)

if __name__ == "__main__":
    main()