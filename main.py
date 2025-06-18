from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QStackedLayout
)
from PySide6.QtGui import QImage, QPainter, QPixmap, QPen, QColor, QFont
from PySide6.QtCore import QTimer, Qt
from camera import Camera
import sys
import numpy as np

class CameraGridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame = None
        self.block_values = None
        self.pixelate_ksize = 7
        self.hide_camera = False  # New attribute

    def set_frame(self, frame, block_values, pixelate_ksize):
        self.frame = frame
        self.block_values = block_values
        self.pixelate_ksize = pixelate_ksize
        self.update()

    def set_hide_camera(self, hide):
        self.hide_camera = hide
        self.update()

    def paintEvent(self, event):
        if self.frame is None or self.block_values is None:
            return

        widget_w, widget_h = self.width(), self.height()
        frame_h, frame_w = self.frame.shape

        painter = QPainter(self)
        x_offset = 0
        y_offset = 0

        # Calculate aspect ratio and offsets
        aspect_ratio = frame_w / frame_h
        if widget_w / widget_h > aspect_ratio:
            pixmap_h = widget_h
            pixmap_w = int(widget_h * aspect_ratio)
        else:
            pixmap_w = widget_w
            pixmap_h = int(widget_w / aspect_ratio)
        x_offset = (widget_w - pixmap_w) // 2
        y_offset = (widget_h - pixmap_h) // 2

        # Draw camera image or white rectangle
        if not self.hide_camera:
            qimg = QImage(self.frame.data, frame_w, frame_h, frame_w, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qimg).scaled(pixmap_w, pixmap_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(x_offset, y_offset, pixmap)
        else:
            painter.fillRect(x_offset, y_offset, pixmap_w, pixmap_h, Qt.white)

        # Draw grid and characters
        block_h, block_w = self.block_values.shape
        cell_w = pixmap_w / block_w
        cell_h = pixmap_h / block_h

        # Draw grid
        pen = QPen(QColor(158, 158, 158), 1)
        painter.setPen(pen)
        for i in range(1, block_w):
            painter.drawLine(x_offset + int(i * cell_w), y_offset, x_offset + int(i * cell_w), y_offset + int(block_h * cell_h))
        for j in range(1, block_h):
            painter.drawLine(x_offset, y_offset + int(j * cell_h), x_offset + int(block_w * cell_w), y_offset + int(j * cell_h))

        # Draw block values as characters
        chars = ['█ ', '@', '#', '&', '%','W', 'V', 'r', 'i', '^', '/', ';', '-', '.', ' ']
        font = QFont("Consolas", int(min(cell_w, cell_h)))
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        for by in range(block_h):
            for bx in range(block_w):
                value = int(self.block_values[by, bx])
                idx = int(value / 255 * (len(chars) - 1))
                text = chars[idx]
                x = x_offset + int(bx * cell_w + cell_w / 2)
                y = y_offset + int(by * cell_h + cell_h / 2)
                painter.drawText(
                    x - painter.fontMetrics().horizontalAdvance(text) // 2,
                    y + painter.fontMetrics().ascent() // 2,
                    text
                )
        painter.end()

    def sizeHint(self):
        if self.frame is not None:
            h, w = self.frame.shape
            return self.frame.shape[::-1]
        return super().sizeHint()

class WhiteOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 255, 128))  # Semi-transparent white
        painter.end()

def main():
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Camera Feed with Pixelation Grid")

    cam = Camera(src=0, width=128, height=56)
    camera_widget = CameraGridWidget()
    camera_widget.setMinimumSize(320, 240)
    white_overlay = WhiteOverlay()
    white_overlay.setMinimumSize(320, 240)

    # Stacked layout for camera/grid and white overlay
    stacked = QStackedLayout()
    stacked.addWidget(camera_widget)   # index 0: camera view
    stacked.addWidget(white_overlay)   # index 1: white overlay

    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(2)
    slider.setMaximum(10)
    slider.setValue(5)
    slider.setTickInterval(1)

    toggle_btn = QPushButton("Hide Camera Feed")
    toggle_btn.setCheckable(True)

    bottom_layout = QHBoxLayout()
    bottom_layout.addWidget(slider)
    bottom_layout.addWidget(toggle_btn)

    layout = QVBoxLayout(window)
    layout.addLayout(stacked)
    layout.addLayout(bottom_layout)
    window.setLayout(layout)
    window.show()

    def on_toggle():
        hide = toggle_btn.isChecked()
        camera_widget.set_hide_camera(hide)
        if hide:
            toggle_btn.setText("Show Camera Feed")
        else:
            toggle_btn.setText("Hide Camera Feed")
    toggle_btn.clicked.connect(on_toggle)

    def update_frame():
        frame, block_values = cam.read(pixelate_ksize=slider.value())
        if frame is not None:
            camera_widget.set_frame(frame, block_values, slider.value())

    timer = QTimer()
    timer.timeout.connect(update_frame)
    timer.start(30)

    app.exec()
    cam.release()

if __name__ == '__main__':
    main()