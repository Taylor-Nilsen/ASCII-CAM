from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLineEdit, QLabel, QFileDialog
)
from PySide6.QtGui import QImage, QPainter, QPixmap, QPen, QColor, QFont, QFontMetrics
from PySide6.QtCore import QTimer, Qt, QThread, Signal
from camera import Camera
import os
import datetime
import cv2
import numpy as np

# ascii characters
char_ramps = {
    "5":  ['█', '▓', '▒', '░', ' '],
    "7":  ['█', '▓', '▒', '░', '+', '.', ' '],
    "9":  ['█', '▓', '▒', '░', '+', '=', '-', '.', ' '],
    "11": ['█', '@', '%', '#', '*', '+', '=', '-', ':', '.', ' '],
    "16": ['$', '@', 'B', '%', '8', '&', 'W', 'M', '#', '*', 'o', 'a', 'h', 'k', 'b', ' ']
}

# char ramp keys in order for slider
char_ramp_keys = ["5", "7", "9", "11", "16"]

# select chars - will be updated dynamically
chars = char_ramps["11"]

class CameraWorker(QThread):
    """Worker thread for camera frame processing"""
    frameReady = Signal(object, object, float)  # frame, block_values, ksize
    
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self.ksize = 3.0
        self.running = False
        
    def set_ksize(self, ksize):
        self.ksize = ksize
        
    def run(self):
        self.running = True
        while self.running:
            frame, block_values = self.camera.read(pixelate_ksize=self.ksize)
            if frame is not None and block_values is not None:
                self.frameReady.emit(frame, block_values, self.ksize)
            self.msleep(33)  # ~30 FPS
            
    def stop(self):
        self.running = False
        self.wait()

class ImageProcessWorker(QThread):
    """Worker thread for uploaded image processing"""
    imageProcessed = Signal(object, object, object)  # frame, block_values, original
    
    def __init__(self):
        super().__init__()
        self.original_img = None
        self.ksize = 3.0
        
    def process_image(self, original_img, ksize):
        self.original_img = original_img
        self.ksize = ksize
        self.start()
        
    def run(self):
        if self.original_img is None:
            return
            
        # Convert to grayscale
        gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        
        # Keep original aspect ratio but scale to reasonable size
        h, w = gray.shape
        max_size = 400  # maximum dimension
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            gray = cv2.resize(gray, (new_w, new_h))
            h, w = gray.shape
        
        # Process with current pixelate setting
        # Convert slider value (4-24) back to original range (1-6)
        actual_ksize = self.ksize / 4.0
        block_width = int(actual_ksize * 3)
        block_height = int(actual_ksize * 5)
        block_w = w // block_width
        block_h = h // block_height
        
        if block_w == 0 or block_h == 0:
            block_w = max(1, block_w)
            block_h = max(1, block_h)
        
        block_values = cv2.resize(
            gray, (block_w, block_h), interpolation=cv2.INTER_LINEAR
        )
        processed_gray = cv2.resize(
            block_values, (w, h), interpolation=cv2.INTER_NEAREST
        )
        
        self.imageProcessed.emit(processed_gray, block_values, self.original_img)

class CameraGridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame = None
        self.block_values = None
        self.pixelate_ksize = 7
        self.hide_camera = False
        self.current_chars = chars  # current character ramp
        self.original_frame = None  # store original frame for uploaded images

    def set_frame(self, frame, block_values, pixelate_ksize, original_frame=None):
        # set frame
        self.frame = frame
        self.block_values = block_values
        self.pixelate_ksize = pixelate_ksize
        if original_frame is not None:
            self.original_frame = original_frame
        self.update()

    def set_hide_camera(self, hide):
        # hide camera
        self.hide_camera = hide
        self.update()

    def set_chars(self, char_ramp):
        # set character ramp
        self.current_chars = char_ramp
        self.update()

    def paintEvent(self, event):
        # draw camera and ascii
        if self.frame is None or self.block_values is None:
            return

        widget_w, widget_h = self.width(), self.height()
        frame_h, frame_w = self.frame.shape

        painter = QPainter(self)
        x_offset = 0
        y_offset = 0

        # fit image
        aspect_ratio = frame_w / frame_h
        if widget_w / widget_h > aspect_ratio:
            pixmap_h = widget_h
            pixmap_w = int(widget_h * aspect_ratio)
        else:
            pixmap_w = widget_w
            pixmap_h = int(widget_w / aspect_ratio)
        x_offset = (widget_w - pixmap_w) // 2
        y_offset = (widget_h - pixmap_h) // 2

        # draw camera or white box
        if not self.hide_camera:
            qimg = QImage(self.frame.data, frame_w, frame_h, frame_w, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qimg).scaled(pixmap_w, pixmap_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(x_offset, y_offset, pixmap)
        else:
            painter.fillRect(x_offset, y_offset, pixmap_w, pixmap_h, Qt.white)

        # draw ascii grid
        block_h, block_w = self.block_values.shape
        cell_w = pixmap_w / block_w
        cell_h = pixmap_h / block_h

        # draw ascii chars with 3x5 aspect ratio consideration
        # Calculate font size based on the smaller dimension to ensure proper fit
        font_size = int(min(cell_w * 0.8, cell_h * 0.6))  # Adjusted for 3x5 aspect ratio
        font = QFont("Consolas", font_size)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        for by in range(block_h):
            for bx in range(block_w):
                value = int(self.block_values[by, bx])
                idx = int(value / 255 * (len(self.current_chars) - 1))
                text = self.current_chars[idx]
                x = x_offset + int(bx * cell_w + cell_w / 2)
                y = y_offset + int(by * cell_h + cell_h / 2)
                painter.drawText(
                    x - painter.fontMetrics().horizontalAdvance(text) // 2,
                    y + painter.fontMetrics().ascent() // 2,
                    text
                )
        painter.end()

    def get_grid_text(self):
        # get ascii as text
        if self.block_values is None:
            return ""
        block_h, block_w = self.block_values.shape
        lines = []
        for by in range(block_h):
            line = ""
            for bx in range(block_w):
                value = int(self.block_values[by, bx])
                idx = int(value / 255 * (len(self.current_chars) - 1))
                line += self.current_chars[idx]
            lines.append(line)
        return "\n".join(lines)

def main():
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("ASCII Cam")

    # camera and ui
    cam = Camera(src=0, width=128, height=56)
    camera_widget = CameraGridWidget()
    camera_widget.setMinimumSize(320, 240)

    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(4)   # 4x more granular: 1*4 = 4
    slider.setMaximum(24)  # 4x more granular: 6*4 = 24  
    slider.setValue(12)    # 4x more granular: 3*4 = 12
    slider.setTickInterval(1)

    # character ramp slider
    char_slider = QSlider(Qt.Horizontal)
    char_slider.setMinimum(0)
    char_slider.setMaximum(4)  # 0-4 for the 5 different char ramps
    char_slider.setValue(3)    # default to "11" char ramp
    char_slider.setTickInterval(1)

    upload_btn = QPushButton("Upload Image")

    toggle_btn = QPushButton("Hide Camera Feed")
    toggle_btn.setCheckable(True)
    freeze_btn = QPushButton("Freeze")
    save_btn = QPushButton("Save Image")
    copy_btn = QPushButton("Copy ASCII Text")

    # Sliders layout - stacked vertically
    sliders_layout = QVBoxLayout()
    sliders_layout.addWidget(QLabel("Block Size:"))
    sliders_layout.addWidget(slider)
    sliders_layout.addWidget(QLabel("Character Set:"))
    sliders_layout.addWidget(char_slider)

    # Buttons layout - two rows
    buttons_layout = QVBoxLayout()
    
    # First row: toggle and freeze/back buttons
    buttons_row1 = QHBoxLayout()
    buttons_row1.addWidget(toggle_btn)
    buttons_row1.addWidget(freeze_btn)
    
    # Back to camera button (initially hidden)
    back_to_cam_btn = QPushButton("Back to Camera")
    back_to_cam_btn.setVisible(False)
    buttons_row1.addWidget(back_to_cam_btn)
    
    # Second row: upload, save, copy buttons
    buttons_row2 = QHBoxLayout()
    buttons_row2.addWidget(upload_btn)
    buttons_row2.addWidget(save_btn)
    buttons_row2.addWidget(copy_btn)
    
    buttons_layout.addLayout(buttons_row1)
    buttons_layout.addLayout(buttons_row2)

    # Controls layout
    controls_layout = QHBoxLayout()
    controls_layout.addLayout(sliders_layout)
    controls_layout.addLayout(buttons_layout)

    main_layout = QVBoxLayout()
    main_layout.addWidget(camera_widget)
    main_layout.addLayout(controls_layout)

    main_ui = QWidget()
    main_ui.setLayout(main_layout)

    window.setLayout(main_layout)
    window.resize(800, 600)
    window.show()

    # save directory storage
    save_dir = {"path": ""}
    
    # uploaded image storage
    uploaded_image = {"original": None, "frame": None, "block_values": None, "active": False}

    frozen = {"active": False, "frame": None, "block_values": None, "ksize": None}

    # Create worker threads
    camera_worker = CameraWorker(cam)
    image_worker = ImageProcessWorker()

    def process_uploaded_image(original_img, ksize):
        # Start image processing in worker thread
        image_worker.process_image(original_img, ksize)

    def on_slider_change(value):
        # Update camera worker ksize (convert from 4-24 to 1-6 range)
        actual_ksize = value / 4.0
        camera_worker.set_ksize(actual_ksize)
        
        # Update frozen display if frozen
        if frozen["active"]:
            frozen["ksize"] = value  # Update stored ksize
            handle_frozen_display()
        
        # update uploaded image when slider changes
        if uploaded_image["active"] and uploaded_image["original"] is not None:
            process_uploaded_image(uploaded_image["original"], value)
    slider.valueChanged.connect(on_slider_change)

    def on_char_slider_change(value):
        # change character ramp
        char_key = char_ramp_keys[value]
        new_chars = char_ramps[char_key]
        camera_widget.set_chars(new_chars)
    char_slider.valueChanged.connect(on_char_slider_change)

    def update_ui_for_mode():
        # Update UI based on current mode
        is_uploaded = uploaded_image["active"]
        is_frozen = frozen["active"]
        freeze_btn.setVisible(not is_uploaded)
        back_to_cam_btn.setVisible(is_uploaded)
        if is_uploaded:
            toggle_btn.setText("Show Image" if toggle_btn.isChecked() else "Hide Image")
            # Stop camera worker and hardware when in upload mode
            camera_worker.stop()
            cam.pause()
        else:
            toggle_btn.setText("Show Camera Feed" if toggle_btn.isChecked() else "Hide Camera Feed")
            # Resume camera when back to camera mode, but only if not frozen
            if not is_frozen:
                cam.resume()
                camera_worker.start()
            elif is_frozen:
                camera_worker.stop()
                cam.pause()

    def on_toggle():
        # hide or show camera/image
        hide = toggle_btn.isChecked()
        camera_widget.set_hide_camera(hide)
        update_ui_for_mode()
    toggle_btn.clicked.connect(on_toggle)

    def on_back_to_cam():
        # go back to camera mode
        uploaded_image["active"] = False
        uploaded_image["original"] = None
        uploaded_image["frame"] = None
        uploaded_image["block_values"] = None
        toggle_btn.setChecked(False)
        update_ui_for_mode()
    back_to_cam_btn.clicked.connect(on_back_to_cam)

    def on_freeze():
        # freeze camera
        frozen["active"] = not frozen["active"]
        if frozen["active"]:
            freeze_btn.setText("Unfreeze")
            frozen["frame"] = camera_widget.frame
            frozen["block_values"] = camera_widget.block_values
            frozen["ksize"] = camera_widget.pixelate_ksize
            # Stop camera worker and pause hardware when frozen
            camera_worker.stop()
            cam.pause()
            # Display the frozen frame
            handle_frozen_display()
        else:
            freeze_btn.setText("Freeze")
            # Resume camera when unfrozen (only if not in upload mode)
            if not uploaded_image["active"]:
                cam.resume()
                camera_worker.start()
    freeze_btn.clicked.connect(on_freeze)

    def on_save():
        # save image
        if not save_dir["path"]:
            # First time saving - ask for directory
            dir_path = QFileDialog.getExistingDirectory(window, "Select Directory to Save Images")
            if not dir_path:
                return  # User cancelled
            save_dir["path"] = dir_path
        
        pixmap = camera_widget.grab()
        now = datetime.datetime.now()
        timestamp = now.strftime("%d %B %Y %I-%M-%S %p")
        filename = f"Capture {timestamp}.png"
        filepath = os.path.join(save_dir["path"], filename)
        pixmap.save(filepath)
    save_btn.clicked.connect(on_save)

    def on_copy():
        # copy ASCII text to clipboard
        ascii_text = camera_widget.get_grid_text()
        if ascii_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(ascii_text)
    copy_btn.clicked.connect(on_copy)

    def on_upload():
        # upload and process an image
        file_path, _ = QFileDialog.getOpenFileName(
            window, 
            "Select Image", 
            "", 
            "Image files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if file_path:
            # Load the image
            img = cv2.imread(file_path)
            if img is not None:
                # Store original image and set active mode
                uploaded_image["original"] = img
                uploaded_image["active"] = True
                toggle_btn.setChecked(False)  # Show image by default
                
                # Update UI mode first
                update_ui_for_mode()
                
                # Process image with current settings (async)
                process_uploaded_image(img, slider.value())
    upload_btn.clicked.connect(on_upload)

    def update_frame(frame, block_values, ksize):
        # Update frame from camera worker
        if not frozen["active"] and not uploaded_image["active"]:
            # Display frame with current slider value
            camera_widget.set_frame(frame, block_values, slider.value())

    def handle_frozen_display():
        # Handle display of frozen frame
        if frozen["active"] and frozen["frame"] is not None and frozen["block_values"] is not None:
            camera_widget.set_frame(frozen["frame"], frozen["block_values"], frozen["ksize"])

    def handle_image_processed(frame, block_values, original):
        # Handle processed image from image worker
        if uploaded_image["active"] and uploaded_image["original"] is not None:
            uploaded_image["frame"] = frame
            uploaded_image["block_values"] = block_values
            # Update the display immediately
            camera_widget.set_frame(frame, block_values, slider.value(), uploaded_image["original"])

    # Connect worker signals
    camera_worker.frameReady.connect(update_frame)
    image_worker.imageProcessed.connect(handle_image_processed)

    # Initialize UI
    update_ui_for_mode()

    # Start camera worker
    camera_worker.start()

    app.exec()
    
    # Clean up
    camera_worker.stop()
    cam.release()

if __name__ == '__main__':
    main()