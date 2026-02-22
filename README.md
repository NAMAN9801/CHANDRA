# 🌙 Project CHANDRA
**Critical Hyperspectral Analysis of Naturally Dark Remote Craters**

A web-based lunar surface analysis tool for detecting and analyzing Permanently Shadowed Regions (PSRs) on the Moon using advanced image processing techniques.

---

## 📋 Quick Start

### What Does CHANDRA Do?
CHANDRA analyzes lunar crater images to:
- Detect dark shadow regions (PSRs) that might contain water ice
- Analyze terrain features like peaks and valleys
- Enhance low-quality images for better visibility
- Generate detailed reports and visualizations

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/NAMAN9801/CHANDRA
cd CHANDRA

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the web server
python server.py
```

Then open **http://localhost:5000** in your browser.

---

## ✨ Features

| Feature | What It Does |
|---------|-------------|
| **Image Upload** | Upload your own lunar crater images |
| **Multiple Detection Methods** | Use 3 different algorithms to find dark regions |
| **Terrain Analysis** | Identify peaks, valleys, and surface roughness |
| **Auto-Enhancement** | Improve image quality automatically |
| **Interactive Visualization** | View results with beautiful 3D interface |
| **Download Results** | Export analysis as high-quality images |

---

## 🔬 How It Works: Image Processing Methods

### 1. **Image Enhancement (CLAHE)**
Enhances low-contrast lunar images to reveal hidden details.
- Makes shadows and craters more visible
- Reduces noise without losing detail
- Works like turning up the contrast dial smartly

### 2. **PSR Detection (3 Methods)**

**Basic Threshold**
- Finds dark pixels below a certain brightness level
- Fast and simple
- Best for clear, high-contrast images

**Adaptive Threshold**
- Adjusts threshold based on surrounding pixels
- Handles varying light conditions
- More accurate for real-world images

**Edge Detection (Canny)**
- Finds sharp boundaries of craters and shadows
- Uses gradient analysis
- Great for crater rim identification

### 3. **Terrain Analysis**
- **Peak Detection**: Finds bright spots (elevated terrain)
- **Valley Detection**: Finds dark spots (depressions)
- **Surface Roughness**: Measures how textured the surface is using localized variation

### 4. **Statistical Analysis**
Calculates metrics like:
- Average brightness and contrast
- Percentage of image that's shadow (PSR coverage)
- Range of pixel values

---

## 🎯 How to Use

### Web Interface
1. Go to http://localhost:5000
2. Click **"Begin Journey"**
3. Upload an image or choose from test gallery
4. Adjust sliders to fine-tune analysis
5. Click **"Analyze"** to see results
6. Download or export your results

### Command Line (Advanced)
```python
from server import ConfigurablePSRAnalyzer
import cv2

# Load image
image = cv2.imread('moon_crater.png', cv2.IMREAD_GRAYSCALE)

# Create analyzer with custom parameters
analyzer = ConfigurablePSRAnalyzer({
    'clahe_clip_limit': 2.0,
    'basic_threshold': 50,
    'edge_sigma': 1.0
})

# Run full analysis
results = analyzer.full_analysis(image)
```

---

## 📊 What You Get

After analysis, you'll see:
- **Original Image** - Your uploaded crater image
- **Enhanced Image** - After brightness/contrast improvement
- **Threshold Detection** - Shadow detection (2 methods)
- **Surface Map** - Shows roughness and terrain
- **Edge Detection** - Crater boundaries
- **Statistics** - Numerical analysis data

---

## 🛠️ Tech Stack

- **Python** - Core language
- **OpenCV** - Image processing
- **Flask** - Web server
- **Three.js** - 3D visualization
- **NumPy, SciPy** - Scientific computing

---

## 📚 Parameters (Adjustable in Web Interface)

| Parameter | What It Controls | Default |
|-----------|------------------|---------|
| CLAHE Clip Limit | Contrast intensity | 2.0 |
| CLAHE Tile Size | Enhancement region size | 8 |
| Basic Threshold | Shadow detection level | 50 |
| Adaptive Block Size | Local comparison window | 11 |
| Edge Sigma | Edge detection sensitivity | 1.0 |

---

## 🎓 Learning Resources

New to image processing? Here's what to know:
- **Threshold**: Separating dark pixels from bright ones
- **Histogram Equalization**: Spreading out pixel values for better contrast
- **Edge Detection**: Finding where images change quickly
- **Peak Detection**: Finding local high points

---

## 📖 Inspiration

This project was inspired by research on lunar surface analysis and PSR detection methods. Named after **Chandrayaan**, India's successful lunar exploration program, CHANDRA combines multiple image processing techniques to automate crater analysis.

---

## 🚀 Features Coming Soon

- [ ] Batch processing for multiple images
- [ ] Machine learning classification
- [ ] Real-time parameter adjustments
- [ ] 3D crater reconstruction
- [ ] API endpoint documentation

---

## 📝 License

MIT License - Feel free to use for educational and research purposes

---

## 👤 Author

**NAMAN DHINGRA**

Repository: https://github.com/NAMAN9801/CHANDRA

---

## 💡 Tips for Best Results

1. **Use high-resolution images** - Better details = better analysis
2. **Grayscale images work best** - Convert colored images to grayscale first
3. **Experiment with sliders** - Different crater types need different settings
4. **Check multiple methods** - No single method is perfect for all cases
5. **Look at statistics** - Numbers tell you how much PSR was detected

---

## ❓ Troubleshooting

**"No features detected"**
- Try increasing the CLAHE clip limit
- Lower the threshold value
- Ensure image quality is good

**"Too much noise in results"**
- Reduce CLAHE clip limit
- Increase threshold value
- Use edge detection instead

**"Server won't start"**
- Check if port 5000 is available
- Verify all dependencies are installed
- Try: `pip install -r requirements.txt --upgrade`

---

**Happy crater analyzing! 🌙**
