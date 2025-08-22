import pyttsx3
import threading
import queue
import time
from typing import Optional, Dict, Any
import os

class EnhancedTTS:
    """Enhanced Text-to-Speech with multiple voice options and better control"""
    
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.engine = None
        self.voice_queue = queue.Queue()
        self.is_speaking = False
        self.speech_thread = None
        
        # Initialize TTS engine
        self._init_engine()
        
        # Start speech thread
        self._start_speech_thread()
    
    def _init_engine(self):
        """Initialize the TTS engine with configuration"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice properties
            self.engine.setProperty('rate', self.cfg.get('rate', 180))
            self.engine.setProperty('volume', self.cfg.get('volume', 0.9))
            
            # Set voice if specified
            voice_name = self.cfg.get('voice', 'default')
            if voice_name != 'default':
                self._set_voice(voice_name)
            
            # Get available voices for reference
            voices = self.engine.getProperty('voices')
            print(f"Available voices: {len(voices)}")
            for i, voice in enumerate(voices):
                print(f"  {i}: {voice.name} ({voice.id})")
                
        except Exception as e:
            print(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def _set_voice(self, voice_name: str):
        """Set a specific voice by name or index"""
        if not self.engine:
            return
            
        voices = self.engine.getProperty('voices')
        
        # Try to find voice by name
        for voice in voices:
            if voice_name.lower() in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                print(f"Set voice to: {voice.name}")
                return
        
        # Try to find voice by index
        try:
            voice_index = int(voice_name)
            if 0 <= voice_index < len(voices):
                self.engine.setProperty('voice', voices[voice_index].id)
                print(f"Set voice to: {voices[voice_index].name}")
                return
        except ValueError:
            pass
        
        print(f"Voice '{voice_name}' not found, using default")
    
    def _start_speech_thread(self):
        """Start the speech processing thread"""
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
    
    def _speech_worker(self):
        """Worker thread for processing speech queue"""
        while True:
            try:
                text = self.voice_queue.get(timeout=1.0)
                if text is None:  # Shutdown signal
                    break
                    
                self._speak_text(text)
                self.voice_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Speech worker error: {e}")
    
    def _speak_text(self, text: str):
        """Actually speak the text"""
        if not self.engine:
            print("TTS engine not available")
            return
            
        try:
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            self.is_speaking = False
    
    def say(self, text: str, priority: bool = False):
        """Queue text for speech synthesis"""
        if not text.strip():
            return
            
        if priority:
            # Clear queue and speak immediately
            while not self.voice_queue.empty():
                try:
                    self.voice_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Speak directly
            self._speak_text(text)
        else:
            # Add to queue
            self.voice_queue.put(text)
    
    def say_async(self, text: str):
        """Speak text asynchronously (non-blocking)"""
        self.say(text, priority=False)
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.engine:
            self.engine.stop()
        self.is_speaking = False
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)"""
        if self.engine:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        if not self.engine:
            return []
            
        voices = self.engine.getProperty('voices')
        return [{'name': v.name, 'id': v.id} for v in voices]
    
    def is_available(self) -> bool:
        """Check if TTS is available"""
        return self.engine is not None
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_speaking()
        if self.voice_queue:
            self.voice_queue.put(None)  # Shutdown signal
        if self.speech_thread:
            self.speech_thread.join(timeout=2.0)

class VoiceManager:
    """Advanced voice management with multiple TTS backends"""
    
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.current_tts = None
        self.voice_profiles = {}
        
        # Initialize primary TTS
        self._init_primary_tts()
        
        # Load voice profiles
        self._load_voice_profiles()
    
    def _init_primary_tts(self):
        """Initialize the primary TTS system"""
        try:
            self.current_tts = EnhancedTTS(self.cfg)
        except Exception as e:
            print(f"Failed to initialize primary TTS: {e}")
    
    def _load_voice_profiles(self):
        """Load predefined voice profiles"""
        self.voice_profiles = {
            'jarvis': {
                'rate': 160,
                'volume': 0.9,
                'voice': 'default',
                'style': 'professional'
            },
            'friendly': {
                'rate': 180,
                'volume': 0.8,
                'voice': 'default',
                'style': 'casual'
            },
            'news': {
                'rate': 140,
                'volume': 0.95,
                'voice': 'default',
                'style': 'formal'
            },
            'whisper': {
                'rate': 120,
                'volume': 0.6,
                'voice': 'default',
                'style': 'quiet'
            }
        }
    
    def set_voice_profile(self, profile_name: str):
        """Set a voice profile"""
        if profile_name not in self.voice_profiles:
            print(f"Voice profile '{profile_name}' not found")
            return
            
        profile = self.voice_profiles[profile_name]
        if self.current_tts:
            self.current_tts.set_rate(profile['rate'])
            self.current_tts.set_volume(profile['volume'])
            self.current_tts._set_voice(profile['voice'])
    
    def say(self, text: str, profile: str = 'jarvis', priority: bool = False):
        """Speak text with specified profile"""
        if profile in self.voice_profiles:
            self.set_voice_profile(profile)
        
        if self.current_tts:
            self.current_tts.say(text, priority)
        else:
            print(f"[TTS]: {text}")
    
    def say_with_emotion(self, text: str, emotion: str = 'neutral'):
        """Speak text with emotional inflection"""
        # Map emotions to voice profiles
        emotion_profiles = {
            'happy': 'friendly',
            'sad': 'whisper',
            'excited': 'friendly',
            'serious': 'news',
            'neutral': 'jarvis'
        }
        
        profile = emotion_profiles.get(emotion, 'jarvis')
        self.say(text, profile)
    
    def stop(self):
        """Stop current speech"""
        if self.current_tts:
            self.current_tts.stop_speaking()
    
    def cleanup(self):
        """Cleanup all TTS resources"""
        if self.current_tts:
            self.current_tts.cleanup()
