# Project CHANDRA

**Crater and Hazard Analysis for Navigation and Discovery of Resources in Astronomy**

A sophisticated lunar surface analysis tool designed for analyzing Permanently Shadowed Regions (PSR) on the Moon. This project provides image enhancement, terrain analysis, and PSR detection capabilities using advanced computer vision techniques.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Web Application](#web-application)
  - [Command Line](#command-line)
  - [Image Enhancement](#image-enhancement)
- [Analysis Methods](#analysis-methods)
- [Output](#output)
- [Technologies Used](#technologies-used)
- [License](#license)

---

## Overview

Project CHANDRA is designed to analyze lunar surface imagery, with a focus on:
- Detecting Permanently Shadowed Regions (PSRs) which are potential sites for water ice deposits
- Analyzing terrain characteristics including surface roughness
- Providing multiple PSR detection methods for comprehensive analysis
- Generating detailed visualizations and statistical reports

---

## Features

- **Image Enhancement**: CLAHE-based contrast enhancement for low-light lunar imagery
- **Multi-Method PSR Detection**:
  - Basic threshold detection
  - Adaptive threshold detection (Gaussian)
  - Canny edge detection
- **Terrain Analysis**:
  - Peak and valley detection
  - Surface roughness mapping
- **Statistical Analysis**: Comprehensive image statistics and PSR coverage metrics
- **Web Interface**: Interactive 3D frontend with image upload capabilities
- **Visualization**: Publication-ready analysis plots

---

## Project Structure

```
CHANDRA/
├── server.py                       # Main Flask web server (deployable)
├── OptimizedPSRAnalyzer.py         # Core PSR analysis module
├── working_psr_image_enhancer.py   # Standalone image enhancement tool
├── app.py                          # Legacy Flask server
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── static/
│   └── index.html                  # Modern web interface with sliders
├── frontend/
│   ├── index.html                  # Landing page with 3D visualization
│   └── upload.html                 # Basic image upload interface
├── assests/
│   ├── psr_image.png               # Sample PSR image
│   └── enhanced_psr_image.png      # Enhanced sample image
├── uploads/                        # Uploaded images (auto-generated)
├── results/                        # Analysis results (auto-generated)
└── psr_analysis_<timestamp>/       # CLI analysis output directories
    ├── analysis_result.png         # Visualization output
    └── statistics.csv              # Statistical data
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CHANDRA
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Required packages:
   - `matplotlib` - Visualization and plotting
   - `numpy` - Numerical computations
   - `opencv-python` - Image processing
   - `pandas` - Data handling and CSV export
   - `scikit-image` - Advanced image analysis
   - `scipy` - Scientific computing
   - `flask` - Web server framework
   - `flask-cors` - Cross-origin resource sharing
   - `pillow` - Image file handling
   - `requests` - HTTP requests

---

## Usage

### Web Application (Recommended)

The main web application provides an interactive interface with real-time parameter adjustment using sliders.

1. **Start the server**
   ```bash
   python server.py
   ```

2. **Open in browser**
   ```
   http://localhost:5000
   ```

3. **Using the Interface**
   - Upload a lunar/PSR image using drag-and-drop or file browser
   - Adjust analysis parameters using the sliders:

   | Parameter | Range | Description |
   |-----------|-------|-------------|
   | CLAHE Clip Limit | 1.0 - 5.0 | Contrast enhancement intensity |
   | CLAHE Tile Size | 4 - 16 | Grid size for local enhancement |
   | Basic Threshold | 10 - 200 | Fixed threshold for PSR detection |
   | Adaptive Block Size | 3 - 31 | Local region size for adaptive threshold |
   | Adaptive C | 0 - 20 | Constant subtracted from mean |
   | Canny Sigma | 0.5 - 5.0 | Edge detection smoothing |
   | Peak Distance | 5 - 50 | Minimum distance between peaks |
   | Roughness Size | 3 - 15 | Kernel size for roughness calculation |

   - Click **Analyze** to run the analysis
   - Click **Export** to download results
   - Click **Reset** to restore default parameters

4. **API Endpoints**
   - `POST /api/upload` - Upload an image
   - `POST /api/analyze` - Run analysis with parameters
   - `POST /api/preview/<type>` - Get single visualization
   - `POST /api/export` - Export full results
   - `GET /api/defaults` - Get default parameters
   - `GET /health` - Health check

### Command Line

Run the analyzer directly on an image:

```bash
python OptimizedPSRAnalyzer.py
```

To analyze a custom image, modify the `image_path` in the `main()` function:

```python
def main():
    analyzer = OptimizedPSRAnalyzer()
    image_path = "path/to/your/image.png"
    result_path = analyzer.analyze_and_visualize(image_path)
```

Or use in your own script:

```python
from OptimizedPSRAnalyzer import OptimizedPSRAnalyzer

analyzer = OptimizedPSRAnalyzer()
result_path = analyzer.analyze_and_visualize("your_image.png")
print(f"Results saved to: {result_path}")
```

### Image Enhancement

For standalone image enhancement:

```bash
python working_psr_image_enhancer.py
```

Customize enhancement parameters:

```python
from working_psr_image_enhancer import enhance_psr_image

enhanced = enhance_psr_image(
    image_path="input.png",
    gamma=1.2,              # Gamma correction (default: 1.2)
    sharpen_strength=0.5    # Sharpening intensity (default: 0.5)
)
```

---

## Analysis Methods

### 1. Image Enhancement (CLAHE)
Contrast Limited Adaptive Histogram Equalization improves visibility in low-contrast lunar imagery while preventing over-amplification of noise.

### 2. PSR Detection Methods

| Method | Description | Best For |
|--------|-------------|----------|
| **Basic Threshold** | Fixed threshold (value < 50) | Clear, high-contrast shadows |
| **Adaptive Threshold** | Gaussian adaptive thresholding | Variable lighting conditions |
| **Edge Detection** | Canny edge detection (σ=1) | Boundary identification |

### 3. Terrain Analysis

- **Peak Detection**: Identifies local maxima (bright spots/elevated terrain)
- **Valley Detection**: Identifies local minima (depressions/shadows)
- **Surface Roughness**: Local standard deviation filter (5x5 kernel) measuring terrain variability

### 4. Statistical Metrics

- **Image Statistics**: Mean, standard deviation, min, max, dynamic range
- **PSR Coverage**: Percentage of image classified as PSR by each method

---

## Output

Each analysis run creates a timestamped directory containing:

### analysis_result.png
A 6-panel visualization showing:
1. Original Image
2. Basic Threshold PSR Detection
3. Adaptive Threshold PSR Detection
4. Surface Roughness Map
5. Edge Detection Results
6. Statistical Summary

### statistics.csv
Tabular data including:
- Image statistics (mean, std, min, max, dynamic range)
- PSR coverage percentages for each detection method

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3** | Core programming language |
| **OpenCV** | Image processing and thresholding |
| **NumPy** | Numerical array operations |
| **SciPy** | Scientific filters (ndimage) |
| **scikit-image** | Advanced image analysis (Canny, peak detection) |
| **Matplotlib** | Visualization and plotting |
| **Pandas** | Data export and CSV handling |
| **Flask** | Web server and API |
| **Three.js** | 3D frontend visualization |

---

## Example Output

```
[12:30:45] Loading image from: assests/psr_image.png
[12:30:45] Enhancing image...
[12:30:45] Detecting PSR regions...
[12:30:46] Analyzing terrain...
[12:30:46] Calculating statistics...
[12:30:46] Saving results...
[12:30:46] Creating visualization...
Analysis complete! Result image saved at: psr_analysis_20260216_123045/analysis_result.png
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

This project is open source and available under the MIT License.

---

## Acknowledgments

- Named after Chandrayaan, India's lunar exploration program
- Designed for lunar PSR analysis and resource detection research
