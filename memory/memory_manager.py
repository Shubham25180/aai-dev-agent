import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from utils.logger import get_action_logger, get_error_logger

class MemoryManager:
    """
    Comprehensive memory management system for AI Dev Agent.
    Handles short-term, long-term, and core behavior memory with automatic persistence.
    Follows AGENT_MANIFEST.md principles for automatic memory management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MemoryManager with configuration and logging.
        
        Args:
            config: Application configuration containing memory paths
        """
        self.config = config
        self.logger = get_action_logger('memory_manager')
        self.error_logger = get_error_logger('memory_manager')
        
        # Memory file paths
        self.memory_path = config.get('paths', {}).get('memory', 'memory')
        self.short_term_path = os.path.join(self.memory_path, 'short_term.json')
        self.long_term_path = os.path.join(self.memory_path, 'long_term.json')
        self.core_behavior_path = os.path.join(self.memory_path, 'core_behavior.json')
        
        # Initialize memory stores
        self.short_term = self._load_memory(self.short_term_path)
        self.long_term = self._load_memory(self.long_term_path)
        self.core_behavior = self._load_memory(self.core_behavior_path)
        
        # Memory update hooks
        self.update_hooks = []
        
        self.logger.info("MemoryManager initialized with all memory stores")

    def _load_memory(self, file_path: str) -> Dict[str, Any]:
        """
        Load memory from file safely.
        
        Args:
            file_path: Path to memory file
            
        Returns:
            Loaded memory dictionary
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
                    self.logger.info(f"Loaded memory from {file_path}", extra={'keys': list(memory.keys())})
                    return memory
            else:
                self.logger.info(f"Memory file not found, creating new: {file_path}")
                return {}
        except Exception as e:
            self.error_logger.error(f"Failed to load memory from {file_path}: {e}")
            return {}

    def _save_memory(self, memory: Dict[str, Any], file_path: str) -> bool:
        """
        Save memory to file safely.
        
        Args:
            memory: Memory dictionary to save
            file_path: Path to save memory file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(memory, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved memory to {file_path}", extra={'keys': list(memory.keys())})
            return True
        except Exception as e:
            self.error_logger.error(f"Failed to save memory to {file_path}: {e}")
            return False

    def update_short_term(self, key: str, value: Any, auto_save: bool = True) -> bool:
        """
        Update short-term memory with new information.
        
        Args:
            key: Memory key
            value: Value to store
            auto_save: Whether to automatically save to file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamp
            if isinstance(value, dict):
                value['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            else:
                value = {
                    'value': value,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            
            self.short_term[key] = value
            self.short_term['last_updated'] = datetime.utcnow().isoformat() + 'Z'
            
            self.logger.info("Updated short-term memory", extra={'key': key})
            
            # Trigger update hooks
            self._trigger_update_hooks('short_term', key, value)
            
            # Auto-save if requested
            if auto_save:
                return self._save_memory(self.short_term, self.short_term_path)
            
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to update short-term memory: {e}")
            return False

    def update_long_term(self, key: str, value: Any, auto_save: bool = True) -> bool:
        """
        Update long-term memory with new information.
        
        Args:
            key: Memory key
            value: Value to store
            auto_save: Whether to automatically save to file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamp and metadata
            if isinstance(value, dict):
                value['timestamp'] = datetime.utcnow().isoformat() + 'Z'
                value['memory_type'] = 'long_term'
            else:
                value = {
                    'value': value,
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'memory_type': 'long_term'
                }
            
            self.long_term[key] = value
            self.long_term['last_updated'] = datetime.utcnow().isoformat() + 'Z'
            
            self.logger.info("Updated long-term memory", extra={'key': key})
            
            # Trigger update hooks
            self._trigger_update_hooks('long_term', key, value)
            
            # Auto-save if requested
            if auto_save:
                return self._save_memory(self.long_term, self.long_term_path)
            
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to update long-term memory: {e}")
            return False

    def update_core_behavior(self, key: str, value: Any, auto_save: bool = True) -> bool:
        """
        Update core behavior memory with new information.
        
        Args:
            key: Memory key
            value: Value to store
            auto_save: Whether to automatically save to file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamp and metadata
            if isinstance(value, dict):
                value['timestamp'] = datetime.utcnow().isoformat() + 'Z'
                value['memory_type'] = 'core_behavior'
            else:
                value = {
                    'value': value,
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'memory_type': 'core_behavior'
                }
            
            self.core_behavior[key] = value
            self.core_behavior['last_updated'] = datetime.utcnow().isoformat() + 'Z'
            
            self.logger.info("Updated core behavior memory", extra={'key': key})
            
            # Trigger update hooks
            self._trigger_update_hooks('core_behavior', key, value)
            
            # Auto-save if requested
            if auto_save:
                return self._save_memory(self.core_behavior, self.core_behavior_path)
            
            return True
            
        except Exception as e:
            self.error_logger.error(f"Failed to update core behavior memory: {e}")
            return False

    def get_short_term(self, key: str, default: Any = None) -> Any:
        """
        Get value from short-term memory.
        
        Args:
            key: Memory key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self.short_term.get(key, default)

    def get_long_term(self, key: str, default: Any = None) -> Any:
        """
        Get value from long-term memory.
        
        Args:
            key: Memory key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self.long_term.get(key, default)

    def get_core_behavior(self, key: str, default: Any = None) -> Any:
        """
        Get value from core behavior memory.
        
        Args:
            key: Memory key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self.core_behavior.get(key, default)

    def get_memory_context(self) -> Dict[str, Any]:
        """
        Get comprehensive memory context for planning.
        
        Returns:
            Dictionary containing all memory context
        """
        return {
            'short_term': {
                'keys': list(self.short_term.keys()),
                'recent_updates': self._get_recent_updates(self.short_term, 5)
            },
            'long_term': {
                'keys': list(self.long_term.keys()),
                'recent_updates': self._get_recent_updates(self.long_term, 5)
            },
            'core_behavior': {
                'keys': list(self.core_behavior.keys()),
                'recent_updates': self._get_recent_updates(self.core_behavior, 5)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def _get_recent_updates(self, memory: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """
        Get recent updates from memory store.
        
        Args:
            memory: Memory dictionary
            count: Number of recent updates to return
            
        Returns:
            List of recent updates
        """
        updates = []
        for key, value in memory.items():
            if key != 'last_updated' and isinstance(value, dict) and 'timestamp' in value:
                updates.append({
                    'key': key,
                    'timestamp': value['timestamp'],
                    'value_type': type(value.get('value', value)).__name__
                })
        
        # Sort by timestamp and return most recent
        updates.sort(key=lambda x: x['timestamp'], reverse=True)
        return updates[:count]

    def add_update_hook(self, hook_func):
        """
        Add a hook function to be called when memory is updated.
        
        Args:
            hook_func: Function to call with (memory_type, key, value) parameters
        """
        self.update_hooks.append(hook_func)
        self.logger.info("Added memory update hook")

    def _trigger_update_hooks(self, memory_type: str, key: str, value: Any):
        """
        Trigger all registered update hooks.
        
        Args:
            memory_type: Type of memory updated
            key: Memory key
            value: Updated value
        """
        for hook in self.update_hooks:
            try:
                hook(memory_type, key, value)
            except Exception as e:
                self.error_logger.error(f"Memory update hook failed: {e}")

    def save_all_memory(self) -> bool:
        """
        Save all memory stores to files.
        
        Returns:
            True if all saves successful, False otherwise
        """
        success = True
        success &= self._save_memory(self.short_term, self.short_term_path)
        success &= self._save_memory(self.long_term, self.long_term_path)
        success &= self._save_memory(self.core_behavior, self.core_behavior_path)
        
        if success:
            self.logger.info("All memory stores saved successfully")
        else:
            self.error_logger.error("Some memory stores failed to save")
        
        return success

    def clear_short_term(self) -> bool:
        """
        Clear short-term memory.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.short_term = {}
            return self._save_memory(self.short_term, self.short_term_path)
        except Exception as e:
            self.error_logger.error(f"Failed to clear short-term memory: {e}")
            return False

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary containing memory statistics
        """
        return {
            'short_term': {
                'total_entries': len(self.short_term),
                'last_updated': self.short_term.get('last_updated'),
                'size_bytes': len(json.dumps(self.short_term))
            },
            'long_term': {
                'total_entries': len(self.long_term),
                'last_updated': self.long_term.get('last_updated'),
                'size_bytes': len(json.dumps(self.long_term))
            },
            'core_behavior': {
                'total_entries': len(self.core_behavior),
                'last_updated': self.core_behavior.get('last_updated'),
                'size_bytes': len(json.dumps(self.core_behavior))
            },
            'total_size_bytes': len(json.dumps(self.short_term)) + len(json.dumps(self.long_term)) + len(json.dumps(self.core_behavior))
        }

    def search_memory(self, query: str, memory_type: str = 'all') -> List[Dict[str, Any]]:
        """
        Search memory for entries containing the query.
        
        Args:
            query: Search query
            memory_type: Type of memory to search ('short_term', 'long_term', 'core_behavior', 'all')
            
        Returns:
            List of matching memory entries
        """
        results = []
        query_lower = query.lower()
        
        memory_stores = {
            'short_term': self.short_term,
            'long_term': self.long_term,
            'core_behavior': self.core_behavior
        }
        
        if memory_type == 'all':
            stores_to_search = memory_stores
        else:
            stores_to_search = {memory_type: memory_stores.get(memory_type, {})}
        
        for store_name, store in stores_to_search.items():
            for key, value in store.items():
                if key == 'last_updated':
                    continue
                
                # Search in key
                if query_lower in key.lower():
                    results.append({
                        'memory_type': store_name,
                        'key': key,
                        'value': value,
                        'match_type': 'key'
                    })
                    continue
                
                # Search in value
                if isinstance(value, dict):
                    value_str = json.dumps(value, default=str).lower()
                else:
                    value_str = str(value).lower()
                
                if query_lower in value_str:
                    results.append({
                        'memory_type': store_name,
                        'key': key,
                        'value': value,
                        'match_type': 'value'
                    })
        
        return results 