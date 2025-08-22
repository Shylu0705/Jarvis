#!/usr/bin/env python3
"""
Enhanced Jarvis Installation Script
Installs all required dependencies for the enhanced features
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_core_dependencies():
    """Install core dependencies"""
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install pyyaml requests", "Installing core packages"),
        ("pip install sounddevice faster-whisper==1.0.3", "Installing audio packages"),
        ("pip install pyttsx3", "Installing TTS"),
        ("pip install mss easyocr Pillow", "Installing screen capture packages"),
        ("pip install pyautogui pynput", "Installing control packages"),
        ("pip install ollama", "Installing Ollama client"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def install_enhanced_dependencies():
    """Install enhanced feature dependencies"""
    commands = [
        ("pip install opencv-python>=4.8.0 opencv-contrib-python>=4.8.0", "Installing OpenCV"),
        ("pip install scikit-learn>=1.3.0", "Installing machine learning packages"),
        ("pip install chromadb>=0.4.0 sentence-transformers>=2.2.0", "Installing memory database"),
        ("pip install librosa>=0.10.0", "Installing audio processing"),
        ("pip install psutil>=5.9.0", "Installing system monitoring"),
        ("pip install nltk>=3.8.0", "Installing natural language processing"),
        ("pip install requests>=2.31.0 beautifulsoup4>=4.12.0", "Installing web scraping"),
        ("pip install pandas>=2.0.0 matplotlib>=3.7.0", "Installing data analysis"),
        ("pip install colorlog>=6.7.0", "Installing logging"),
        ("pip install python-dotenv>=1.0.0", "Installing configuration management"),
        ("pip install aiohttp>=3.8.0", "Installing async support"),
        ("pip install pydub>=0.25.0", "Installing audio processing"),
    ]
    
    # Windows-specific packages
    if platform.system() == "Windows":
        commands.extend([
            ("pip install pywin32>=306", "Installing Windows integration"),
            ("pip install python-magic-bin>=0.4.14", "Installing Windows file processing"),
        ])
    else:
        commands.append(("pip install python-magic>=0.4.27", "Installing file processing"))
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️  Warning: {description} failed, but continuing...")
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("🔄 Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        print("✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"⚠️  Warning: Failed to download NLTK data: {e}")
        return True  # Not critical

def create_directories():
    """Create necessary directories"""
    directories = [
        "jarvis_memory",
        "logs",
        "config",
        "data"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"ℹ️  Directory already exists: {directory}")

def check_ollama():
    """Check if Ollama is available"""
    print("🔄 Checking Ollama availability...")
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is not available")
            print("Please install Ollama from https://ollama.com/")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        print("Please install Ollama from https://ollama.com/")
        return False

def suggest_ollama_models():
    """Suggest Ollama models to install"""
    print("\n📋 Suggested Ollama models to install:")
    print("ollama pull llama3:8b-instruct-q4_0    # Good balance of speed/quality")
    print("ollama pull qwen2.5:7b-instruct        # Fast and capable")
    print("ollama pull mistral:7b-instruct        # Good general purpose")
    print("ollama pull llama3.1:8b-instruct       # Latest Llama model")

def main():
    """Main installation function"""
    print("🚀 Enhanced Jarvis Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install core dependencies
    print("\n📦 Installing core dependencies...")
    if not install_core_dependencies():
        print("❌ Core dependencies installation failed")
        sys.exit(1)
    
    # Install enhanced dependencies
    print("\n🔧 Installing enhanced dependencies...")
    install_enhanced_dependencies()
    
    # Download NLTK data
    print("\n📚 Downloading language data...")
    download_nltk_data()
    
    # Check Ollama
    print("\n🤖 Checking Ollama...")
    ollama_available = check_ollama()
    
    print("\n" + "=" * 50)
    print("✅ Installation completed!")
    
    if ollama_available:
        print("\n🎯 Next steps:")
        print("1. Install an Ollama model:")
        suggest_ollama_models()
        print("\n2. Run Enhanced Jarvis:")
        print("   python -m app.enhanced_main")
        print("\n3. Try the new features:")
        print("   - 'what do you see in the camera?'")
        print("   - 'memory stats'")
        print("   - 'help'")
    else:
        print("\n⚠️  Please install Ollama before running Jarvis:")
        print("   https://ollama.com/")
    
    print("\n📖 For more information, see QUICK_START_ENHANCED.md")
    print("🎉 Enjoy your enhanced Jarvis!")

if __name__ == "__main__":
    main()
