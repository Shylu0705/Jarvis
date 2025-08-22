from inputs.screen import ScreenReader
from control.desktop import DesktopControl

class Toolbelt:
    def __init__(self, cfg):
        self.screen = ScreenReader(cfg["screen"])
        self.ctrl = DesktopControl(cfg["controls"])

    def read_screen_text(self):
        text = self.screen.ocr_screen()
        return f"Screen OCR:\n{text[:2000]}" if text else "No text detected."

    def type_text(self, text: str):
        self.ctrl.type_text(text)

    def click(self, x=None, y=None):
        self.ctrl.click(x, y)

    def move_mouse(self, x, y):
        self.ctrl.move_mouse(x, y)
