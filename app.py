import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, 
                           QVBoxLayout, QWidget, QSlider, QHBoxLayout, QFrame, QGroupBox)
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from psr_image_enhancer import enhance_psr_image

class PSREnhancerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PSR Image Processing Tool')
        self.setGeometry(100, 100, 1000, 800)
        
        # Set the application color scheme
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#1e1e1e'))
        palette.setColor(QPalette.WindowText, QColor('#ffffff'))
        palette.setColor(QPalette.Base, QColor('#2d2d2d'))
        palette.setColor(QPalette.AlternateBase, QColor('#353535'))
        palette.setColor(QPalette.Text, QColor('#ffffff'))
        palette.setColor(QPalette.Button, QColor('#353535'))
        palette.setColor(QPalette.ButtonText, QColor('#ffffff'))
        self.setPalette(palette)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Create left panel for controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_panel.setMinimumWidth(250)
        left_layout = QVBoxLayout(left_panel)

        # Control Panel Title
        title_label = QLabel("Image Controls")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: #404040;
                border-radius: 5px;
            }
        """)
        left_layout.addWidget(title_label)

        # Buttons
        self.loadButton = QPushButton('Load Image')
        self.loadButton.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """)
        self.loadButton.clicked.connect(self.loadImage)
        left_layout.addWidget(self.loadButton)

        # Slider Group
        slider_group = QGroupBox("Enhancement Parameters")
        slider_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #404040;
                border-radius: 5px;
                margin-top: 20px;
                padding: 15px;
                color: white;
                background-color: #353535;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
                color: white;
                background-color: #353535;
            }
            QLabel {
                color: white;
            }
        """)
        slider_layout = QVBoxLayout()

        # Gamma Slider
        gamma_label = QLabel("Gamma Correction:")
        self.gammaSlider = QSlider(Qt.Horizontal)
        self.gammaSlider.setMinimum(50)
        self.gammaSlider.setMaximum(200)
        self.gammaSlider.setValue(120)
        self.gammaSlider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #404040;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0066cc;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        self.gammaSlider.valueChanged.connect(self.updateGammaLabel)
        self.gammaLabel = QLabel('1.20')
        slider_layout.addWidget(gamma_label)
        slider_layout.addWidget(self.gammaSlider)
        slider_layout.addWidget(self.gammaLabel)

        # Sharpen Slider
        sharpen_label = QLabel("Sharpness:")
        self.sharpenSlider = QSlider(Qt.Horizontal)
        self.sharpenSlider.setMinimum(0)
        self.sharpenSlider.setMaximum(100)
        self.sharpenSlider.setValue(50)
        self.sharpenSlider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #404040;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0066cc;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        self.sharpenSlider.valueChanged.connect(self.updateSharpenLabel)
        self.sharpenLabel = QLabel('50%')
        slider_layout.addWidget(sharpen_label)
        slider_layout.addWidget(self.sharpenSlider)
        slider_layout.addWidget(self.sharpenLabel)

        slider_group.setLayout(slider_layout)
        left_layout.addWidget(slider_group)

        # Enhance Button
        self.enhanceButton = QPushButton('Enhance Image')
        self.enhanceButton.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.enhanceButton.clicked.connect(self.enhanceImage)
        left_layout.addWidget(self.enhanceButton)

        left_layout.addStretch()

        # Create right panel for image display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Image display
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.imageLabel.setMinimumSize(600, 600)
        right_layout.addWidget(self.imageLabel)

        # Add panels to main layout
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)

        self.imagePath = None

    def updateGammaLabel(self, value):
        gamma = value / 100
        self.gammaLabel.setText(f'Gamma: {gamma:.2f}')

    def updateSharpenLabel(self, value):
        self.sharpenLabel.setText(f'Sharpness: {value}%')

    def loadImage(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Load Image", "", 
                                                "Images (*.png *.jpg *.bmp);;All Files (*)", options=options)
        if fileName:
            self.imagePath = fileName
            self.displayImage(fileName)

    def enhanceImage(self):
        if self.imagePath:
            gamma = self.gammaSlider.value() / 100
            sharpen_strength = self.sharpenSlider.value() / 100
            enhanced_image = enhance_psr_image(self.imagePath, gamma=gamma, sharpen_strength=sharpen_strength)
            self.displayImage(enhanced_image, is_enhanced=True)

    def displayImage(self, image, is_enhanced=False):
        if is_enhanced:
            height, width = image.shape
            bytes_per_line = width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:
            q_image = QImage(image)
        
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.imageLabel.size(), 
                                    Qt.KeepAspectRatio, 
                                    Qt.SmoothTransformation)
        self.imageLabel.setPixmap(scaled_pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PSREnhancerApp()
    ex.show()
    sys.exit(app.exec_())