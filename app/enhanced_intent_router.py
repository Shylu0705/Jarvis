import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class EnhancedIntentRouter:
    """Enhanced intent recognition with better natural language understanding"""
    
    def __init__(self, cfg: dict = None):
        self.cfg = cfg or {}
        
        # Intent patterns
        self.intent_patterns = {
            'screen_read': [
                r'(what|show|tell).*(on|in).*(screen|display)',
                r'(read|scan).*(screen|display)',
                r'(what).*(see|visible)',
                r'(screen|display).*(content|text|information)'
            ],
            'webcam_analyze': [
                r'(what|show|tell).*(see|visible).*(camera|webcam)',
                r'(analyze|check).*(camera|webcam|video)',
                r'(who|what).*(front|back).*(camera)',
                r'(camera|webcam).*(scene|view)'
            ],
            'type_text': [
                r'type\s*[:.]?\s*(.+)',
                r'write\s*[:.]?\s*(.+)',
                r'enter\s*[:.]?\s*(.+)',
                r'input\s*[:.]?\s*(.+)'
            ],
            'click': [
                r'click\s+(?:at\s+)?(\d+)\s*[,.]?\s*(\d+)',
                r'click\s+(?:position\s+)?(\d+)\s*[,.]?\s*(\d+)',
                r'click\s+(?:coordinates\s+)?(\d+)\s*[,.]?\s*(\d+)'
            ],
            'move_mouse': [
                r'move\s+(?:mouse\s+)?(?:to\s+)?(\d+)\s*[,.]?\s*(\d+)',
                r'position\s+(?:mouse\s+)?(?:at\s+)?(\d+)\s*[,.]?\s*(\d+)',
                r'go\s+(?:to\s+)?(\d+)\s*[,.]?\s*(\d+)'
            ],
            'search_web': [
                r'(search|find|look\s+up).*(?:for\s+)?(.+)',
                r'(google|bing|search\s+engine).*(.+)',
                r'(web\s+search|internet\s+search).*(.+)'
            ],
            'open_app': [
                r'open\s+(.+)',
                r'launch\s+(.+)',
                r'start\s+(.+)',
                r'run\s+(.+)'
            ],
            'file_operation': [
                r'(create|make|new)\s+(file|document|folder).*(.+)',
                r'(save|store)\s+(.+)',
                r'(delete|remove)\s+(.+)',
                r'(copy|duplicate)\s+(.+)'
            ],
            'system_control': [
                r'(shutdown|turn\s+off|power\s+down)',
                r'(restart|reboot)',
                r'(sleep|suspend)',
                r'(volume|sound|mute|unmute)',
                r'(brightness|screen\s+brightness)'
            ],
            'memory_query': [
                r'(remember|recall|what\s+did).*(we\s+talk|conversation)',
                r'(history|past|previous).*(conversation|talk)',
                r'(memory|memories).*(search|find)'
            ],
            'preference_setting': [
                r'(set|change|update).*(preference|setting)',
                r'(voice|speech|tts).*(rate|speed|volume)',
                r'(camera|webcam).*(resolution|quality)'
            ],
            'help_request': [
                r'(help|assist|support)',
                r'(what\s+can\s+you\s+do|capabilities|features)',
                r'(how\s+to|instructions|guide)'
            ],
            'general_chat': [
                r'(hello|hi|hey|greetings)',
                r'(how\s+are\s+you|how\s+you\s+doing)',
                r'(thank\s+you|thanks|appreciate)',
                r'(goodbye|bye|see\s+you|later)'
            ]
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            'coordinates': r'(\d+)\s*[,.]?\s*(\d+)',
            'url': r'https?://[^\s]+',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'time': r'\b\d{1,2}:\d{2}\s*(?:AM|PM)?\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        }
        
        # Confidence scoring weights
        self.confidence_weights = {
            'exact_match': 1.0,
            'pattern_match': 0.8,
            'keyword_match': 0.6,
            'partial_match': 0.4
        }
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parse user input and extract intent with confidence scoring"""
        text = text.lower().strip()
        
        # Initialize result
        result = {
            'type': 'unknown',
            'confidence': 0.0,
            'entities': {},
            'raw_text': text,
            'timestamp': datetime.now().isoformat()
        }
        
        # Try exact matches first
        exact_intent = self._check_exact_matches(text)
        if exact_intent:
            result.update(exact_intent)
            result['confidence'] = self.confidence_weights['exact_match']
            return result
        
        # Try pattern matching
        pattern_intent = self._check_pattern_matches(text)
        if pattern_intent:
            result.update(pattern_intent)
            result['confidence'] = self.confidence_weights['pattern_match']
            return result
        
        # Try keyword matching
        keyword_intent = self._check_keyword_matches(text)
        if keyword_intent:
            result.update(keyword_intent)
            result['confidence'] = self.confidence_weights['keyword_match']
            return result
        
        # Extract entities even for unknown intents
        result['entities'] = self._extract_entities(text)
        
        return result
    
    def _check_exact_matches(self, text: str) -> Optional[Dict[str, Any]]:
        """Check for exact phrase matches"""
        exact_phrases = {
            'what\'s on my screen': {'type': 'screen_read'},
            'read screen': {'type': 'screen_read'},
            'take screenshot': {'type': 'screen_read'},
            'what do you see': {'type': 'webcam_analyze'},
            'camera view': {'type': 'webcam_analyze'},
            'help': {'type': 'help_request'},
            'what can you do': {'type': 'help_request'},
            'goodbye': {'type': 'general_chat', 'subtype': 'farewell'},
            'thank you': {'type': 'general_chat', 'subtype': 'gratitude'}
        }
        
        for phrase, intent in exact_phrases.items():
            if text == phrase:
                return intent
        
        return None
    
    def _check_pattern_matches(self, text: str) -> Optional[Dict[str, Any]]:
        """Check for pattern matches"""
        best_match = None
        best_confidence = 0.0
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    confidence = len(match.group(0)) / len(text)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = {
                            'type': intent_type,
                            'match': match.group(0),
                            'groups': match.groups()
                        }
        
        if best_match:
            # Extract specific data based on intent type
            intent_data = self._extract_intent_data(best_match['type'], best_match['groups'], text)
            best_match.update(intent_data)
            return best_match
        
        return None
    
    def _check_keyword_matches(self, text: str) -> Optional[Dict[str, Any]]:
        """Check for keyword-based intent classification"""
        keywords = {
            'screen_read': ['screen', 'display', 'read', 'what', 'see', 'visible'],
            'webcam_analyze': ['camera', 'webcam', 'video', 'photo', 'picture'],
            'type_text': ['type', 'write', 'enter', 'input', 'text'],
            'click': ['click', 'tap', 'press', 'select'],
            'move_mouse': ['move', 'position', 'go', 'mouse', 'cursor'],
            'search_web': ['search', 'find', 'google', 'look', 'web'],
            'open_app': ['open', 'launch', 'start', 'run', 'app', 'program'],
            'file_operation': ['file', 'document', 'folder', 'save', 'delete', 'copy'],
            'system_control': ['shutdown', 'restart', 'volume', 'brightness', 'system'],
            'memory_query': ['remember', 'recall', 'history', 'memory', 'past'],
            'preference_setting': ['preference', 'setting', 'configure', 'voice', 'camera'],
            'help_request': ['help', 'assist', 'support', 'how', 'what'],
            'general_chat': ['hello', 'hi', 'how', 'thank', 'goodbye', 'bye']
        }
        
        best_intent = None
        best_score = 0.0
        
        for intent_type, intent_keywords in keywords.items():
            score = 0
            for keyword in intent_keywords:
                if keyword in text:
                    score += 1
            
            if score > 0:
                normalized_score = score / len(intent_keywords)
                if normalized_score > best_score:
                    best_score = normalized_score
                    best_intent = intent_type
        
        if best_intent and best_score > 0.3:  # Threshold for keyword matching
            return {
                'type': best_intent,
                'keyword_score': best_score
            }
        
        return None
    
    def _extract_intent_data(self, intent_type: str, groups: tuple, text: str) -> Dict[str, Any]:
        """Extract specific data based on intent type"""
        data = {}
        
        if intent_type == 'type_text':
            if groups and len(groups) > 0:
                data['text'] = groups[0].strip()
        
        elif intent_type == 'click':
            if len(groups) >= 2:
                try:
                    data['x'] = int(groups[0])
                    data['y'] = int(groups[1])
                except ValueError:
                    pass
        
        elif intent_type == 'move_mouse':
            if len(groups) >= 2:
                try:
                    data['x'] = int(groups[0])
                    data['y'] = int(groups[1])
                except ValueError:
                    pass
        
        elif intent_type == 'search_web':
            if groups and len(groups) > 0:
                data['query'] = groups[-1].strip()  # Last group is usually the search query
        
        elif intent_type == 'open_app':
            if groups and len(groups) > 0:
                data['app_name'] = groups[0].strip()
        
        elif intent_type == 'file_operation':
            if groups and len(groups) > 0:
                data['operation'] = groups[0].strip()
                if len(groups) > 1:
                    data['target'] = groups[1].strip()
        
        return data
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def get_intent_description(self, intent_type: str) -> str:
        """Get a human-readable description of an intent"""
        descriptions = {
            'screen_read': 'Read and analyze screen content',
            'webcam_analyze': 'Analyze webcam feed',
            'type_text': 'Type text input',
            'click': 'Click at coordinates',
            'move_mouse': 'Move mouse cursor',
            'search_web': 'Search the web',
            'open_app': 'Open application',
            'file_operation': 'Perform file operations',
            'system_control': 'Control system settings',
            'memory_query': 'Query conversation history',
            'preference_setting': 'Change user preferences',
            'help_request': 'Request help or information',
            'general_chat': 'General conversation',
            'unknown': 'Unknown or unclear intent'
        }
        
        return descriptions.get(intent_type, 'Unknown intent')
    
    def get_suggested_actions(self, intent_type: str) -> List[str]:
        """Get suggested actions for an intent"""
        suggestions = {
            'screen_read': [
                'Take a screenshot',
                'Extract text from screen',
                'Analyze screen content'
            ],
            'webcam_analyze': [
                'Capture webcam frame',
                'Detect faces in view',
                'Analyze scene content'
            ],
            'type_text': [
                'Extract text to type',
                'Confirm text content',
                'Execute typing action'
            ],
            'click': [
                'Validate coordinates',
                'Execute click action',
                'Provide feedback'
            ],
            'help_request': [
                'Show available commands',
                'Explain capabilities',
                'Provide usage examples'
            ]
        }
        
        return suggestions.get(intent_type, [])
    
    def validate_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance intent with additional context"""
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'suggestions': []
        }
        
        intent_type = intent.get('type')
        
        # Validate specific intent types
        if intent_type == 'click':
            x, y = intent.get('x'), intent.get('y')
            if x is None or y is None:
                validation_result['is_valid'] = False
                validation_result['warnings'].append('Missing coordinates for click action')
            elif not (0 <= x <= 3000 and 0 <= y <= 2000):  # Reasonable screen bounds
                validation_result['warnings'].append('Coordinates may be outside screen bounds')
        
        elif intent_type == 'type_text':
            text = intent.get('text', '')
            if not text:
                validation_result['is_valid'] = False
                validation_result['warnings'].append('No text specified for typing')
            elif len(text) > 1000:
                validation_result['warnings'].append('Text is very long, consider breaking it up')
        
        elif intent_type == 'search_web':
            query = intent.get('query', '')
            if not query:
                validation_result['is_valid'] = False
                validation_result['warnings'].append('No search query specified')
        
        # Add suggestions
        validation_result['suggestions'] = self.get_suggested_actions(intent_type)
        
        return validation_result
