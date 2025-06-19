import cv2

class Camera:
    def __init__(self, src=0, width=128, height=56):
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read(self, pixelate_ksize=None):
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.flip(gray, 1)  # Mirror horizontally
        block_values = None
        if pixelate_ksize is not None:
            h, w = gray.shape
            block_w = w // pixelate_ksize
            block_h = h // pixelate_ksize
            block_values = cv2.resize(
                gray, (block_w, block_h), interpolation=cv2.INTER_LINEAR
            )
            gray = cv2.resize(
                block_values, (w, h), interpolation=cv2.INTER_NEAREST
            )
        return gray, block_values
    

    def release(self):
        self.cap.release()