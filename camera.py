import cv2

class Camera:
    def __init__(self, src=0, width=128, height=56):
        self.src = src
        self.width = width
        self.height = height
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.is_paused = False

    def read(self, pixelate_ksize=None):
        if self.is_paused or not self.cap.isOpened():
            return None, None
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.flip(gray, 1)  # Mirror horizontally
        block_values = None
        if pixelate_ksize is not None:
            h, w = gray.shape
            # Use 3x5 aspect ratio for blocks (3 wide, 5 tall)
            block_width = int(pixelate_ksize * 3)
            block_height = int(pixelate_ksize * 5)
            block_w = w // block_width
            block_h = h // block_height
            # Ensure minimum of 1 for block dimensions
            block_w = max(1, block_w)
            block_h = max(1, block_h)
            block_values = cv2.resize(
                gray, (block_w, block_h), interpolation=cv2.INTER_LINEAR
            )
            gray = cv2.resize(
                block_values, (w, h), interpolation=cv2.INTER_NEAREST
            )
        return gray, block_values

    def pause(self):
        """Pause the camera by releasing the capture"""
        self.is_paused = True
        if self.cap.isOpened():
            self.cap.release()

    def resume(self):
        """Resume the camera by reopening the capture"""
        self.is_paused = False
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.src)
            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
    

    def release(self):
        if self.cap.isOpened():
            self.cap.release()