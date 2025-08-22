
import pyttsx3

class TTS:
    def __init__(self, cfg):
        self.engine = pyttsx3.init()
        rate = cfg.get("rate", 180)
        self.engine.setProperty("rate", rate)

    def say(self, text: str):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[TTS Error] {e}")
