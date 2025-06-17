import sys
from PySide6.QtWidgets import QApplication, QLabel, QSizePolicy
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, Qt
from camera import Camera

# Main application entry

def main():
    app = QApplication(sys.argv)

    # Create a resizable label window
    label = QLabel()
    label.setWindowTitle("Camera Feed")
    label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    label.setAlignment(Qt.AlignCenter)
    # Ensure an initial visible size
    label.resize(640, 480)
    label.setMinimumSize(320, 240)
    label.setMaximumSize(1280, 960)
    label.show()

    # Initialize camera with desired resolution (no audio)
    cam = Camera(src=0, width=640, height=480)

    def update_frame():
        frame = cam.read()
        if frame is None:
            return
        h, w, ch = frame.shape
        # Wrap numpy frame in a QImage
        qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        # Scale pixmap to label size, keeping aspect ratio
        pix = QPixmap.fromImage(qimg).scaled(
            label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        label.setPixmap(pix)

    # Timer to trigger updates at ~33 FPS
    timer = QTimer()
    timer.timeout.connect(update_frame)
    timer.start(30)

    # Start event loop
    app.exec()
    cam.release()

if __name__ == '__main__':
    main()