from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QStackedLayout, QLineEdit, QLabel, QFileDialog
)
from PySide6.QtGui import QImage, QPainter, QPixmap, QPen, QColor, QFont, QFontMetrics
from PySide6.QtCore import QTimer, Qt
from camera import Camera
import os
import datetime

char_ramps = {
    "11": ['█', '@', '%', '#', '*', '+', '=', '-', ':', '.', ' '],
    "5":  ['█', '▓', '▒', '░', ' ']
}

# Change this line to switch ramps
chars = char_ramps["11"]

class CameraGridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame = None
        self.block_values = None
        self.pixelate_ksize = 7
        self.hide_camera = False

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

        # Draw block values as characters
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

    def get_grid_text(self):
        if self.block_values is None:
            return ""
        block_h, block_w = self.block_values.shape
        lines = []
        for by in range(block_h):
            line = ""
            for bx in range(block_w):
                value = int(self.block_values[by, bx])
                idx = int(value / 255 * (len(chars) - 1))
                line += chars[idx]
            lines.append(line)
        return "\n".join(lines)

class StartupOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_dir = ""
        layout = QVBoxLayout(self)
        layout.addStretch()
        label = QLabel("Select a directory to save images:")
        layout.addWidget(label, alignment=Qt.AlignCenter)

        # Directory selector
        dir_layout = QHBoxLayout()
        self.dir_edit = QLineEdit()
        self.dir_edit.setReadOnly(True)
        dir_btn = QPushButton("Browse...")
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(dir_btn)
        layout.addLayout(dir_layout)

        # Next button
        self.next_btn = QPushButton("Next")
        self.next_btn.setEnabled(False)
        layout.addWidget(self.next_btn, alignment=Qt.AlignCenter)
        layout.addStretch()

        dir_btn.clicked.connect(self.pick_dir)
        self.dir_edit.textChanged.connect(self.check_valid)
    
    def pick_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.dir_edit.setText(dir_path)
            self.selected_dir = dir_path

    def check_valid(self):
        self.next_btn.setEnabled(bool(self.dir_edit.text()))

def main():
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("ASCII Cam")

    # --- Main UI setup ---
    cam = Camera(src=0, width=128, height=56)
    camera_widget = CameraGridWidget()
    camera_widget.setMinimumSize(320, 240)

    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(2)
    slider.setMaximum(10)
    slider.setValue(5)
    slider.setTickInterval(1)

    toggle_btn = QPushButton("Hide Camera Feed")
    toggle_btn.setCheckable(True)
    freeze_btn = QPushButton("Freeze")
    save_btn = QPushButton("Save Image")

    bottom_layout = QHBoxLayout()
    bottom_layout.addWidget(slider)
    bottom_layout.addWidget(toggle_btn)
    bottom_layout.addWidget(freeze_btn)
    bottom_layout.addWidget(save_btn)

    main_layout = QVBoxLayout()
    main_layout.addWidget(camera_widget)
    main_layout.addLayout(bottom_layout)

    main_ui = QWidget()
    main_ui.setLayout(main_layout)

    # --- Startup overlay ---
    overlay = StartupOverlay()

    # --- Stacked layout ---
    stacked = QStackedLayout()
    stacked.addWidget(overlay)   # index 0: overlay
    stacked.addWidget(main_ui)   # index 1: main UI

    window.setLayout(stacked)
    window.resize(800, 600)
    window.show()

    # --- Only show main UI after valid dir is picked ---
    save_dir = {"path": ""}

    def on_next():
        save_dir["path"] = overlay.selected_dir
        stacked.setCurrentIndex(1)
    overlay.next_btn.clicked.connect(on_next)

    frozen = {"active": False, "frame": None, "block_values": None, "ksize": None}

    def on_slider_change(value):
        pass
    slider.valueChanged.connect(on_slider_change)

    def on_toggle():
        hide = toggle_btn.isChecked()
        camera_widget.set_hide_camera(hide)
        if hide:
            toggle_btn.setText("Show Camera Feed")
        else:
            toggle_btn.setText("Hide Camera Feed")
    toggle_btn.clicked.connect(on_toggle)

    def on_freeze():
        frozen["active"] = not frozen["active"]
        if frozen["active"]:
            freeze_btn.setText("Unfreeze")
            frozen["frame"] = camera_widget.frame
            frozen["block_values"] = camera_widget.block_values
            frozen["ksize"] = camera_widget.pixelate_ksize
        else:
            freeze_btn.setText("Freeze")
    freeze_btn.clicked.connect(on_freeze)

    def on_save():
        if save_dir["path"]:
            # Grab a snapshot of the camera widget
            pixmap = camera_widget.grab()
            now = datetime.datetime.now()
            timestamp = now.strftime("%d %B %Y %I-%M-%S %p")
            filename = f"Capture {timestamp}.png"
            filepath = os.path.join(save_dir["path"], filename)
            pixmap.save(filepath)
    save_btn.clicked.connect(on_save)

    def update_frame():
        if frozen["active"] and frozen["frame"] is not None and frozen["block_values"] is not None:
            camera_widget.set_frame(frozen["frame"], frozen["block_values"], frozen["ksize"])
        else:
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