# Enhanced Jarvis - Quick Start Guide

## 🚀 What's New

Your Jarvis has been enhanced with:
- **Webcam Integration**: Real-time video analysis and face detection
- **Enhanced TTS**: Multiple voice profiles and emotional responses
- **Long-term Memory**: Persistent conversation history with ChromaDB
- **Better Intent Recognition**: Advanced natural language understanding
- **Enhanced Context**: Multi-modal awareness and reasoning

## 📋 Prerequisites

1. **Python 3.10+** with virtual environment
2. **Ollama** with a local model (llama3:8b-instruct recommended)
3. **Webcam** (optional but recommended)
4. **Windows 10/11** (tested on your system)

## ⚡ Quick Installation

### 1. Install New Dependencies
```powershell
# Activate your virtual environment
.\.venv\Scripts\Activate.ps1

# Install enhanced dependencies
pip install -r requirements.txt
```

### 2. Install ChromaDB (for memory)
```powershell
pip install chromadb sentence-transformers
```

### 3. Install OpenCV (for webcam)
```powershell
pip install opencv-python opencv-contrib-python
```

### 4. Install Machine Learning Libraries
```powershell
pip install scikit-learn
```

## 🎯 Running Enhanced Jarvis

### Option 1: Enhanced Console Mode (Recommended)
```powershell
python -m app.enhanced_main
```

### Option 2: Voice Mode
1. Edit `config.yaml` and set `use_voice_loop: true`
2. Run: `python -m app.enhanced_main`

## 🎮 New Commands to Try

### Webcam Commands
```
"what do you see in the camera?"
"analyze the webcam feed"
"who is in front of the camera?"
"describe the scene"
```

### Memory Commands
```
"memory stats"
"search memories for python"
"what did we talk about yesterday?"
"recall our conversation about coding"
```

### Enhanced Voice Commands
```
"speak in friendly voice"
"use news voice"
"whisper mode"
"normal jarvis voice"
```

### Advanced Commands
```
"what's on my screen and what do you see in the camera?"
"remember that I prefer dark mode"
"search for our conversation about AI"
"help"
```

## 🔧 Configuration

### Webcam Settings
Edit `config.yaml`:
```yaml
webcam:
  camera_index: 0       # Try 1, 2 if webcam doesn't work
  resolution: [640, 480]
  fps: 30
  enable_face_detection: true
  enable_object_detection: true
```

### Voice Profiles
```yaml
enhanced_tts:
  default_profile: "jarvis"
  voice_profiles:
    jarvis:
      rate: 160
      volume: 0.9
    friendly:
      rate: 180
      volume: 0.8
    news:
      rate: 140
      volume: 0.95
    whisper:
      rate: 120
      volume: 0.6
```

### Memory Settings
```yaml
memory:
  db_path: "./jarvis_memory"
  max_memories: 10000
  auto_cleanup_days: 30
```

## 🎨 Voice Profiles

- **Jarvis**: Professional, clear (default)
- **Friendly**: Warm, conversational
- **News**: Formal, authoritative
- **Whisper**: Quiet, intimate

## 🧠 Memory Features

- **Conversation History**: Remembers all chats
- **Semantic Search**: Find past conversations by meaning
- **User Preferences**: Learns your settings
- **Action Logging**: Tracks what Jarvis has done
- **Context Awareness**: Uses past conversations for better responses

## 🔍 Troubleshooting

### Webcam Issues
```powershell
# Check available cameras
python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"

# Try different camera index in config.yaml
camera_index: 1  # or 2, 3, etc.
```

### Memory Database Issues
```powershell
# Reset memory database
rm -rf ./jarvis_memory
# Restart Jarvis to recreate database
```

### Voice Issues
```powershell
# Check available system voices
python -c "import pyttsx3; engine = pyttsx3.init(); print([v.name for v in engine.getProperty('voices')])"
```

### Performance Issues
```yaml
# Reduce memory usage
memory:
  max_memories: 1000  # Instead of 10000

# Lower webcam resolution
webcam:
  resolution: [320, 240]
  fps: 15
```

## 📊 Monitoring

### Check Memory Stats
```
memory stats
```

### View Logs
```powershell
# Check log file
Get-Content jarvis.log -Tail 20
```

### Performance Monitoring
- Memory usage: Check `jarvis_memory` folder size
- CPU usage: Monitor during webcam operations
- Response time: Should be < 2 seconds for simple queries

## 🎯 Next Steps

1. **Try all voice profiles**: Test different personalities
2. **Experiment with webcam**: Try face detection and scene analysis
3. **Build memory**: Have conversations to populate the database
4. **Customize settings**: Adjust voice, memory, and webcam parameters
5. **Explore advanced features**: Use semantic search and context awareness

## 🆘 Getting Help

- Check the logs: `jarvis.log`
- Memory issues: `memory stats` command
- Webcam problems: Try different `camera_index`
- Voice issues: Check system voice availability
- Performance: Reduce resolution/memory limits

## 🚀 Advanced Features Coming Soon

- Object detection with YOLO
- Gesture recognition
- Emotion detection
- GUI interface
- API integrations
- Mobile companion app

Enjoy your enhanced Jarvis! 🤖✨
