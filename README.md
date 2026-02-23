# 🌙 Project CHANDRA
**Critical Hyperspectral Analysis of Naturally Dark Remote Craters**

Project CHANDRA is a web-based lunar surface analysis tool that detects and analyzes Permanently Shadowed Regions (PSRs) on the Moon. This project draws inspiration from [Luna](https://github.com/GreNxNja/Luna) (SIH 1732), which focused on enhancing feeble light from PSR regions of lunar craters captured by Chandrayaan-2's OHRC. We built upon Luna's foundation and extended it with a full-featured web interface, multiple detection algorithms (basic threshold, adaptive threshold, and Canny edge detection), real-time terrain analysis with peak/valley detection, interactive 3D visualization powered by Three.js, adjustable parameters via UI sliders, and a deployable architecture on Render.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Image Upload** | Upload your own lunar crater images |
| **Multiple Detection Methods** | 3 different algorithms to detect shadow regions |
| **Terrain Analysis** | Identify peaks, valleys, and surface roughness |
| **Auto-Enhancement** | CLAHE-based image quality improvement |
| **3D Visualization** | Interactive Three.js-powered interface |
| **Export Results** | Download analysis as high-quality images |

---

## � Quick Start

```bash
# Clone and setup
git clone https://github.com/NAMAN9801/CHANDRA
cd CHANDRA
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run
python server.py
```
---

## 🔬 How It Works

CHANDRA enhances low-contrast lunar images using CLAHE (Contrast Limited Adaptive Histogram Equalization) and then runs PSR detection through three methods basic thresholding for simple high-contrast images, adaptive thresholding for varying lighting conditions, and Canny edge detection for crater boundary identification. It also performs terrain analysis by detecting peaks, valleys, and computing surface roughness, along with statistical metrics like shadow coverage percentage and contrast values.

---

## 🌐 Deployment

**Live Demo:** [project-chandra.onrender.com](https://project-chandra.onrender.com)

> **Note:** On Render's free tier, only lightweight test images (test1, test5) work in the gallery. Larger images (test2–test4) require running the project locally.

---

##  Contributors

| Name | GitHub |
|------|--------|
| Naman Dhingra | [https://github.com/NAMAN9801](https://github.com/NAMAN9801) |
| Krrish Sharma |  |
| Sayam Sharma |  |
| Divya Sharma |  |
| Ritvik Sarswat | [https://github.com/chaRITSzard](https://github.com/chaRITSzard) |
---

## 📝 License

MIT License — Free to use for educational and research purposes.
