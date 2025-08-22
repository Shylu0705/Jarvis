
import time
import pyautogui

class DesktopControl:
    def __init__(self, cfg):
        self.type_delay = cfg.get("type_delay", 0.01)

    def type_text(self, text: str):
        pyautogui.typewrite(text, interval=self.type_delay)

    def click(self, x=None, y=None):
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y)
        else:
            pyautogui.click()

    def move_mouse(self, x, y):
        pyautogui.moveTo(x, y, duration=0.1)
