import chromadb
import json
import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

class EnhancedMemory:
    """Enhanced memory system with ChromaDB for long-term storage and semantic search"""
    
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.db_path = cfg.get("db_path", "./jarvis_memory")
        self.collection_name = cfg.get("collection_name", "jarvis_memories")
        self.max_memories = cfg.get("max_memories", 10000)
        
        # Initialize ChromaDB
        self._init_database()
        
        # In-memory conversation buffer
        self.conversation_buffer = []
        self.max_buffer_size = cfg.get("max_buffer_size", 50)
        
        # Memory categories
        self.categories = {
            'conversation': 'User-assistant conversations',
            'action': 'Actions performed by the assistant',
            'observation': 'Screen and webcam observations',
            'user_preference': 'User preferences and settings',
            'knowledge': 'General knowledge and facts',
            'task': 'Tasks and workflows'
        }
    
    def _init_database(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(path=self.db_path)
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                print(f"Connected to existing memory collection: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Jarvis AI Assistant Memory"}
                )
                print(f"Created new memory collection: {self.collection_name}")
            
            # Get collection info
            count = self.collection.count()
            print(f"Memory database contains {count} entries")
            
        except Exception as e:
            print(f"Failed to initialize memory database: {e}")
            self.client = None
            self.collection = None
    
    def add_memory(self, content: str, category: str = 'conversation', 
                   metadata: Dict[str, Any] = None, embedding: List[float] = None) -> str:
        """Add a new memory entry"""
        if not self.collection:
            return None
            
        # Generate unique ID
        memory_id = self._generate_id(content, category)
        
        # Prepare metadata
        meta = {
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'content_length': len(content)
        }
        if metadata:
            meta.update(metadata)
        
        # Add to ChromaDB
        try:
            self.collection.add(
                documents=[content],
                metadatas=[meta],
                ids=[memory_id],
                embeddings=[embedding] if embedding else None
            )
            
            # Add to conversation buffer if it's a conversation
            if category == 'conversation':
                self._add_to_buffer(content, meta)
            
            return memory_id
            
        except Exception as e:
            print(f"Failed to add memory: {e}")
            return None
    
    def search_memories(self, query: str, category: str = None, 
                       n_results: int = 5) -> List[Dict[str, Any]]:
        """Search memories by semantic similarity"""
        if not self.collection:
            return []
        
        try:
            # Build where clause for category filter
            where_clause = None
            if category:
                where_clause = {"category": category}
            
            # Search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
            
            # Format results
            memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    memory = {
                        'content': doc,
                        'metadata': results['metadatas'][0][i],
                        'id': results['ids'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else None
                    }
                    memories.append(memory)
            
            return memories
            
        except Exception as e:
            print(f"Failed to search memories: {e}")
            return []
    
    def get_recent_memories(self, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent memories by timestamp"""
        if not self.collection:
            return []
        
        try:
            # Get all memories
            results = self.collection.get()
            
            # Filter by category if specified
            if category:
                filtered_memories = []
                for i, meta in enumerate(results['metadatas']):
                    if meta.get('category') == category:
                        memory = {
                            'content': results['documents'][i],
                            'metadata': meta,
                            'id': results['ids'][i]
                        }
                        filtered_memories.append(memory)
                memories = filtered_memories
            else:
                memories = [
                    {
                        'content': results['documents'][i],
                        'metadata': results['metadatas'][i],
                        'id': results['ids'][i]
                    }
                    for i in range(len(results['documents']))
                ]
            
            # Sort by timestamp (newest first)
            memories.sort(key=lambda x: x['metadata'].get('timestamp', ''), reverse=True)
            
            return memories[:limit]
            
        except Exception as e:
            print(f"Failed to get recent memories: {e}")
            return []
    
    def get_context_for_conversation(self, current_query: str, 
                                   max_context: int = 5) -> str:
        """Get relevant context for current conversation"""
        # Search for relevant memories
        relevant_memories = self.search_memories(current_query, 'conversation', max_context)
        
        # Get recent conversation buffer
        recent_buffer = self.conversation_buffer[-max_context:] if self.conversation_buffer else []
        
        # Combine and format context
        context_parts = []
        
        if relevant_memories:
            context_parts.append("Relevant past conversations:")
            for memory in relevant_memories:
                context_parts.append(f"- {memory['content'][:200]}...")
        
        if recent_buffer:
            context_parts.append("\nRecent conversation:")
            for entry in recent_buffer:
                context_parts.append(f"- {entry['content'][:200]}...")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def add_conversation(self, user_input: str, assistant_response: str):
        """Add a conversation turn to memory"""
        # Add user input
        self.add_memory(
            content=f"User: {user_input}",
            category='conversation',
            metadata={'speaker': 'user', 'turn': 'input'}
        )
        
        # Add assistant response
        self.add_memory(
            content=f"Assistant: {assistant_response}",
            category='conversation',
            metadata={'speaker': 'assistant', 'turn': 'response'}
        )
    
    def add_observation(self, observation: str, source: str = 'screen'):
        """Add an observation (screen, webcam, etc.)"""
        self.add_memory(
            content=observation,
            category='observation',
            metadata={'source': source, 'type': 'visual'}
        )
    
    def add_action(self, action: str, result: str = None):
        """Add an action performed by the assistant"""
        content = f"Action: {action}"
        if result:
            content += f" | Result: {result}"
        
        self.add_memory(
            content=content,
            category='action',
            metadata={'type': 'system_action'}
        )
    
    def add_user_preference(self, preference: str, value: Any):
        """Add a user preference"""
        self.add_memory(
            content=f"User preference: {preference} = {value}",
            category='user_preference',
            metadata={'type': 'setting'}
        )
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get all user preferences"""
        preferences = self.search_memories("user preference", 'user_preference', 50)
        
        prefs = {}
        for memory in preferences:
            content = memory['content']
            if 'User preference:' in content:
                try:
                    # Parse preference from content
                    parts = content.split('User preference:')[1].strip().split(' = ')
                    if len(parts) == 2:
                        key, value = parts[0].strip(), parts[1].strip()
                        prefs[key] = value
                except:
                    continue
        
        return prefs
    
    def _add_to_buffer(self, content: str, metadata: Dict[str, Any]):
        """Add to conversation buffer"""
        self.conversation_buffer.append({
            'content': content,
            'metadata': metadata,
            'timestamp': time.time()
        })
        
        # Trim buffer if too large
        if len(self.conversation_buffer) > self.max_buffer_size:
            self.conversation_buffer = self.conversation_buffer[-self.max_buffer_size:]
    
    def _generate_id(self, content: str, category: str) -> str:
        """Generate a unique ID for a memory"""
        timestamp = str(time.time())
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{category}_{timestamp}_{content_hash}"
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory database statistics"""
        if not self.collection:
            return {'error': 'Database not available'}
        
        try:
            count = self.collection.count()
            
            # Get category distribution
            results = self.collection.get()
            categories = {}
            for meta in results['metadatas']:
                cat = meta.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            return {
                'total_memories': count,
                'categories': categories,
                'buffer_size': len(self.conversation_buffer),
                'database_path': self.db_path
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup_old_memories(self, days_old: int = 30):
        """Remove memories older than specified days"""
        if not self.collection:
            return
        
        try:
            cutoff_time = time.time() - (days_old * 24 * 3600)
            
            # Get all memories
            results = self.collection.get()
            
            # Find old memories
            old_ids = []
            for i, meta in enumerate(results['metadatas']):
                timestamp_str = meta.get('timestamp', '')
                try:
                    timestamp = datetime.fromisoformat(timestamp_str).timestamp()
                    if timestamp < cutoff_time:
                        old_ids.append(results['ids'][i])
                except:
                    continue
            
            # Delete old memories
            if old_ids:
                self.collection.delete(ids=old_ids)
                print(f"Deleted {len(old_ids)} old memories")
            
        except Exception as e:
            print(f"Failed to cleanup old memories: {e}")
    
    def export_memories(self, filepath: str):
        """Export all memories to a JSON file"""
        if not self.collection:
            return
        
        try:
            results = self.collection.get()
            
            memories = []
            for i in range(len(results['documents'])):
                memory = {
                    'id': results['ids'][i],
                    'content': results['documents'][i],
                    'metadata': results['metadatas'][i]
                }
                memories.append(memory)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(memories, f, indent=2, ensure_ascii=False)
            
            print(f"Exported {len(memories)} memories to {filepath}")
            
        except Exception as e:
            print(f"Failed to export memories: {e}")
    
    def import_memories(self, filepath: str):
        """Import memories from a JSON file"""
        if not self.collection:
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            for memory in memories:
                self.add_memory(
                    content=memory['content'],
                    category=memory['metadata'].get('category', 'conversation'),
                    metadata=memory['metadata']
                )
            
            print(f"Imported {len(memories)} memories from {filepath}")
            
        except Exception as e:
            print(f"Failed to import memories: {e}")
