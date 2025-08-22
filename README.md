
# Jarvis-Local (All-Local Personal AI Assistant)

This is a **starter, modular skeleton** for a local-only personal assistant that can:
- Chat via a local LLM (default: **Ollama** running `llama3` or any local model),
- Listen to your microphone (**STT** via `faster-whisper`),
- Speak responses (**TTS** via `pyttsx3` – simple and fully offline),
- See your screen (**mss** screenshot + **EasyOCR** for on-screen text),
- Control your computer (**pyautogui** for keyboard/mouse),
- Orchestrate simple "tools" (screen read, click, type) from natural language.

> This is intentionally minimal and beginner-friendly. You can swap components later
> (e.g., use `piper` for better TTS, `whisper.cpp` for STT, YOLO for vision, etc.).

---

## 0) System Requirements (Windows-friendly)

- NVIDIA GPU (you have RTX 4080 Mobile)
- Python 3.10 or 3.11 (64-bit)
- (Recommended) A virtual environment
- **Ollama** for local LLMs (Windows installer available)

Optional (later):
- Tesseract OCR (not required; we use EasyOCR here)
- CUDA-enabled PyTorch (installed automatically by `torch` CPU by default; see below to enable GPU)

---

## 1) Quick Start

### A) Install Ollama
1. Download Ollama for Windows from: https://ollama.com/
2. After installing, open **PowerShell** and run (pick one model to begin):
   ```powershell
   ollama pull llama3:8b-instruct
   ```
   You can also try: `qwen2.5:7b-instruct`, `mistral`, etc.

### B) Create and activate a Python venv
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### C) Install dependencies
```powershell
pip install -r requirements.txt
```
> If you want GPU-accelerated **EasyOCR**/**torch**, install a CUDA build of PyTorch:
> Visit https://pytorch.org/get-started/locally/ and run the suggested `pip install` command,
> then re-run `pip install -r requirements.txt` to ensure the rest is satisfied.

### D) Configure
Open `config.yaml` to review/edit:
- Which Ollama model to use
- Hotkeys and safety settings

### E) Run
```powershell
python -m app.main
```
Try speaking: “**What’s on my screen?**” or “**Type: Hello Professor**”.

---

## 2) What’s Included

```
jarvis-local/
├── app/
│   ├── main.py                  # Orchestrator (loop)
│   ├── intent_router.py         # Lightweight rule-based intents
│   ├── tools.py                 # Tool functions (screen_read, type_text, click, etc.)
│   └── memory.py                # Simple in-session scratch memory
├── core/
│   └── llm.py                   # LLM client (Ollama by default)
├── io/
│   ├── audio_in.py              # Microphone capture + STT (faster-whisper)
│   ├── tts_out.py               # Offline TTS (pyttsx3)
│   └── screen.py                # Screen capture + OCR (mss + EasyOCR)
├── control/
│   └── desktop.py               # Keyboard/mouse actions with pyautogui
├── config.yaml                  # Central configuration
├── requirements.txt
└── README.md
```

---

## 3) Safety

- **Confirmation layer**: by default the assistant *asks* before executing risky actions like clicking or typing large text. You can answer "yes" or "no".
- **Action log**: actions are printed in the console.
- **No code execution**: Disabled by default (you can add later with strong sandboxing).

---

## 4) Next Steps / Upgrades

- Swap STT to `whisper.cpp` for even faster local speech recognition.
- Replace `pyttsx3` with `piper` or `Coqui TTS` for better voices.
- Add object detection (YOLOv8/RT-DETR) to click UI elements by description.
- Add long-term memory with a local vector DB (Chroma) and document ingestion.
- Add a small GUI (e.g., PySide6 or a web UI via Gradio).

Happy building!
