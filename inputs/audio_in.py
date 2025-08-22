
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

class SpeechRecognizer:
    def __init__(self, cfg):
        self.rate = cfg.get("sample_rate", 16000)
        model_size = cfg.get("stt_model", "medium")
        # device="cuda" if GPU is configured, else "cpu"
        try:
            self.model = WhisperModel(model_size, device="cuda", compute_type="float16")
        except Exception:
            self.model = WhisperModel(model_size, device="cpu")
        self.blocksize = 4000
        self.buffer = np.zeros(0, dtype=np.float32)
        self.mic_device = cfg.get("mic_device", None)

    def listen_stream(self):
        """Generator yielding recognized phrases from the mic in a loop."""
        def callback(indata, frames, time, status):
            if status:
                print(status, flush=True)
            self.chunks.append(indata.copy())

        while True:
            self.chunks = []
            with sd.InputStream(channels=1, samplerate=self.rate, blocksize=self.blocksize,
                                dtype="float32", callback=callback, device=self.mic_device):
                # collect ~2.5 seconds
                sd.sleep(2500)
            audio = np.concatenate(self.chunks, axis=0).flatten()
            if len(audio) == 0:
                yield ""
                continue

            segments, info = self.model.transcribe(audio, language=None)
            text = "".join([seg.text for seg in segments]).strip()
            yield text
