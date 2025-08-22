import time
import queue
import threading
import sys
import yaml
import logging
from typing import Dict, Any, Optional

# Import enhanced modules
from app.enhanced_intent_router import EnhancedIntentRouter
from app.tools import Toolbelt
from memory.enhanced_memory import EnhancedMemory
from core.llm import LocalLLM
from inputs.audio_in import SpeechRecognizer
from inputs.enhanced_tts import VoiceManager
from inputs.webcam import WebcamInput

class EnhancedJarvis:
    """Enhanced Jarvis AI Assistant with webcam, better TTS, and long-term memory"""
    
    def __init__(self, config_path: str = "config.yaml"):
        # Load configuration
        self.cfg = self._load_config(config_path)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize subsystems
        self._init_subsystems()
        
        # State management
        self.is_running = False
        self.current_context = {}
        
        self.logger.info("Enhanced Jarvis initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
            return {}
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = self.cfg.get("app", {}).get("log_level", "INFO")
        log_file = self.cfg.get("app", {}).get("log_file", "jarvis.log")
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("Jarvis")
    
    def _init_subsystems(self):
        """Initialize all subsystems"""
        try:
            # Core LLM
            self.llm = LocalLLM(self.cfg["llm"])
            self.logger.info("LLM initialized")
            
            # Enhanced intent recognition
            self.intent_router = EnhancedIntentRouter(self.cfg.get("intent_recognition", {}))
            self.logger.info("Intent router initialized")
            
            # Enhanced memory
            self.memory = EnhancedMemory(self.cfg.get("memory", {}))
            self.logger.info("Memory system initialized")
            
            # Tools
            self.tools = Toolbelt(self.cfg)
            self.logger.info("Tools initialized")
            
            # Enhanced TTS
            self.voice_manager = VoiceManager(self.cfg.get("enhanced_tts", {}))
            self.logger.info("Voice manager initialized")
            
            # Webcam (if enabled)
            self.webcam = None
            if self.cfg.get("app", {}).get("enable_webcam", True):
                try:
                    self.webcam = WebcamInput(self.cfg.get("webcam", {}))
                    self.logger.info("Webcam initialized")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize webcam: {e}")
            
            # Speech recognition (for voice mode)
            self.stt = None
            if self.cfg.get("app", {}).get("use_voice_loop", False):
                try:
                    self.stt = SpeechRecognizer(self.cfg["audio"])
                    self.logger.info("Speech recognition initialized")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize STT: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize subsystems: {e}")
            raise
    
    def start(self):
        """Start Jarvis"""
        self.is_running = True
        self.logger.info("Starting Enhanced Jarvis")
        
        # Start webcam if available
        if self.webcam:
            self.webcam.start()
        
        # Choose interaction mode
        if self.cfg.get("app", {}).get("use_voice_loop", False) and self.stt:
            self._voice_loop()
        else:
            self._console_loop()
    
    def stop(self):
        """Stop Jarvis"""
        self.is_running = False
        self.logger.info("Stopping Jarvis")
        
        # Stop webcam
        if self.webcam:
            self.webcam.stop()
        
        # Cleanup voice manager
        if self.voice_manager:
            self.voice_manager.cleanup()
    
    def _voice_loop(self):
        """Voice interaction loop"""
        self.voice_manager.say("Voice mode ready. Say something.", "jarvis")
        
        try:
            for transcript in self.stt.listen_stream():
                if not self.is_running:
                    break
                    
                text = transcript.strip()
                if not text:
                    continue
                
                print(f"\n[You]: {text}")
                self._handle_user_input(text)
                
        except KeyboardInterrupt:
            self.logger.info("Voice loop interrupted")
        except Exception as e:
            self.logger.error(f"Voice loop error: {e}")
    
    def _console_loop(self):
        """Console interaction loop"""
        print("Enhanced Jarvis Console Mode")
        print("Available commands:")
        print("- what's on my screen?")
        print("- what do you see in the camera?")
        print("- type: Hello Professor")
        print("- click 500 400")
        print("- move 1000 500")
        print("- help")
        print("- memory stats")
        print("Press Ctrl+C to exit.\n")
        
        try:
            while self.is_running:
                user_input = input("You> ").strip()
                if not user_input:
                    continue
                
                self._handle_user_input(user_input)
                
        except KeyboardInterrupt:
            self.logger.info("Console loop interrupted")
        except Exception as e:
            self.logger.error(f"Console loop error: {e}")
    
    def _handle_user_input(self, user_input: str):
        """Handle user input with enhanced processing"""
        try:
            # Parse intent
            intent = self.intent_router.parse_intent(user_input)
            print(f"[Intent]: {intent['type']} (confidence: {intent['confidence']:.2f})")
            
            # Validate intent
            validation = self.intent_router.validate_intent(intent)
            if not validation['is_valid']:
                for warning in validation['warnings']:
                    print(f"[Warning]: {warning}")
            
            # Execute action based on intent
            tool_result = self._execute_intent(intent)
            
            # Get context for LLM
            context = self._build_context(user_input, intent, tool_result)
            
            # Generate response
            response = self._generate_response(user_input, context, intent)
            
            # Speak response
            self.voice_manager.say(response, "jarvis")
            print(f"[Assistant]: {response}")
            
            # Store in memory
            self.memory.add_conversation(user_input, response)
            
        except Exception as e:
            error_msg = f"Error processing input: {e}"
            self.logger.error(error_msg)
            self.voice_manager.say("I encountered an error processing your request.", "jarvis")
            print(f"[Error]: {error_msg}")
    
    def _execute_intent(self, intent: Dict[str, Any]) -> Optional[str]:
        """Execute actions based on intent"""
        intent_type = intent.get('type')
        
        try:
            if intent_type == 'screen_read':
                result = self.tools.read_screen_text()
                self.memory.add_observation(result, 'screen')
                return result
            
            elif intent_type == 'webcam_analyze':
                if self.webcam:
                    result = self.webcam.get_scene_description()
                    self.memory.add_observation(result, 'webcam')
                    return result
                else:
                    return "Webcam is not available"
            
            elif intent_type == 'type_text':
                text = intent.get('text', '')
                if text:
                    if self._should_confirm_action('type_text'):
                        print(f"[Confirm] Type this? -> {text!r}  (y/n)")
                        if input("> ").strip().lower() != 'y':
                            return "User cancelled typing."
                    
                    self.tools.type_text(text)
                    result = f"Typed: {text}"
                    self.memory.add_action('type_text', result)
                    return result
                else:
                    return "No text specified for typing"
            
            elif intent_type == 'click':
                x, y = intent.get('x'), intent.get('y')
                if x is not None and y is not None:
                    if self._should_confirm_action('click'):
                        print(f"[Confirm] Click at ({x}, {y})? (y/n)")
                        if input("> ").strip().lower() != 'y':
                            return "User cancelled click."
                    
                    self.tools.click(x, y)
                    result = f"Clicked at ({x}, {y})"
                    self.memory.add_action('click', result)
                    return result
                else:
                    self.tools.click()
                    result = "Clicked at current position"
                    self.memory.add_action('click', result)
                    return result
            
            elif intent_type == 'move_mouse':
                x, y = intent.get('x'), intent.get('y')
                if x is not None and y is not None:
                    self.tools.move_mouse(x, y)
                    result = f"Moved mouse to ({x}, {y})"
                    self.memory.add_action('move_mouse', result)
                    return result
            
            elif intent_type == 'help_request':
                return self._get_help_text()
            
            elif intent_type == 'memory_query':
                return self._handle_memory_query(intent)
            
            elif intent_type == 'general_chat':
                return None  # Let LLM handle general conversation
            
            else:
                return None  # Unknown intent, let LLM handle
                
        except Exception as e:
            self.logger.error(f"Error executing intent {intent_type}: {e}")
            return f"Error executing {intent_type}: {e}"
    
    def _should_confirm_action(self, action_type: str) -> bool:
        """Check if action requires confirmation"""
        require_confirmation = self.cfg.get("app", {}).get("require_confirmation_for", [])
        return action_type in require_confirmation or self.cfg.get("controls", {}).get("confirm_actions", True)
    
    def _build_context(self, user_input: str, intent: Dict[str, Any], tool_result: Optional[str]) -> str:
        """Build context for LLM"""
        context_parts = []
        
        # Add memory context
        memory_context = self.memory.get_context_for_conversation(user_input)
        if memory_context:
            context_parts.append(f"Memory Context:\n{memory_context}")
        
        # Add current observations
        if self.webcam and intent.get('type') != 'webcam_analyze':
            webcam_context = self.webcam.get_scene_description()
            if webcam_context != "No webcam feed available":
                context_parts.append(f"Current Webcam: {webcam_context}")
        
        # Add tool result
        if tool_result:
            context_parts.append(f"Tool Result: {tool_result}")
        
        # Add intent information
        intent_desc = self.intent_router.get_intent_description(intent.get('type', 'unknown'))
        context_parts.append(f"Detected Intent: {intent_desc}")
        
        return "\n\n".join(context_parts)
    
    def _generate_response(self, user_input: str, context: str, intent: Dict[str, Any]) -> str:
        """Generate LLM response"""
        system_prompt = (
            "You are Jarvis, an enhanced AI assistant with the following capabilities:\n"
            "- Screen reading and analysis\n"
            "- Webcam scene analysis\n"
            "- Desktop control (typing, clicking, mouse movement)\n"
            "- Long-term memory and conversation history\n"
            "- Multiple voice profiles and emotional responses\n\n"
            "Available tools: screen_read, webcam_analyze, type_text, click, move_mouse\n"
            "Always be helpful, concise, and natural in your responses.\n"
            "If the user asks about your capabilities, explain what you can do."
        )
        
        # Add context to system prompt
        if context:
            system_prompt += f"\n\nCurrent Context:\n{context}"
        
        # Get response from LLM
        response = self.llm.chat(
            system=system_prompt,
            history=self.memory.conversation_buffer[-10:],  # Last 10 turns
            tool_result=context
        )
        
        return response
    
    def _get_help_text(self) -> str:
        """Get help information"""
        return (
            "I'm Jarvis, your enhanced AI assistant! Here's what I can do:\n\n"
            "🔍 **Perception & Analysis:**\n"
            "- Read and analyze your screen content\n"
            "- Analyze webcam feed and detect faces/objects\n"
            "- Understand natural language commands\n\n"
            "🖱️ **Desktop Control:**\n"
            "- Type text: 'type: Hello World'\n"
            "- Click: 'click 500 400' or 'click here'\n"
            "- Move mouse: 'move 1000 500'\n\n"
            "🧠 **Memory & Context:**\n"
            "- Remember our conversations\n"
            "- Learn your preferences\n"
            "- Provide contextual responses\n\n"
            "🎤 **Voice Interaction:**\n"
            "- Multiple voice profiles (jarvis, friendly, news, whisper)\n"
            "- Emotional responses\n"
            "- Natural conversation flow\n\n"
            "Try commands like:\n"
            "- 'What's on my screen?'\n"
            "- 'What do you see in the camera?'\n"
            "- 'Type: Hello Professor'\n"
            "- 'Click 500 400'\n"
            "- 'Memory stats'\n"
            "- 'Help'"
        )
    
    def _handle_memory_query(self, intent: Dict[str, Any]) -> str:
        """Handle memory-related queries"""
        query = intent.get('raw_text', '')
        
        if 'stats' in query or 'statistics' in query:
            stats = self.memory.get_memory_stats()
            return f"Memory Statistics: {stats}"
        
        elif 'search' in query or 'find' in query:
            # Extract search terms from query
            search_terms = query.replace('search', '').replace('find', '').strip()
            if search_terms:
                results = self.memory.search_memories(search_terms, n_results=3)
                if results:
                    return f"Found {len(results)} relevant memories:\n" + "\n".join([f"- {r['content'][:100]}..." for r in results])
                else:
                    return "No relevant memories found."
        
        else:
            # Get recent memories
            recent = self.memory.get_recent_memories(limit=5)
            if recent:
                return f"Recent memories:\n" + "\n".join([f"- {r['content'][:100]}..." for r in recent])
            else:
                return "No recent memories found."

def main():
    """Main entry point"""
    try:
        jarvis = EnhancedJarvis()
        jarvis.start()
    except KeyboardInterrupt:
        print("\nShutting down Jarvis...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'jarvis' in locals():
            jarvis.stop()

if __name__ == "__main__":
    main()
