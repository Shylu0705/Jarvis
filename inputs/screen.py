
from mss import mss
from PIL import Image
import numpy as np
import easyocr
import io
import yaml

class ScreenReader:
    def __init__(self, cfg):
        self.mon = cfg.get("capture_region", None)  # None = full screen
        langs = cfg.get("ocr_langs", ["en"])
        # Try GPU if available; easyocr will fall back to CPU if it fails
        try:
            self.reader = easyocr.Reader(langs, gpu=True)
        except Exception:
            self.reader = easyocr.Reader(langs, gpu=False)

    def screenshot(self):
        with mss() as sct:
            shot = sct.grab(self.mon) if self.mon else sct.grab(sct.monitors[1])
            img = Image.frombytes("RGB", (shot.width, shot.height), shot.rgb)
            return img

    def ocr_screen(self):
        img = self.screenshot()
        arr = np.array(img)
        results = self.reader.readtext(arr, detail=0, paragraph=True)
        return "\n".join(results)
