import threading
from collections import deque
from datetime import datetime
from typing import List, Dict, Any, Optional

class ShortTermMemoryManager:
    def __init__(self, max_history_size: int = 50, max_actions_size: int = 100):
        self._max_history = max_history_size
        self._max_actions = max_actions_size
        
        # Thread safety locks
        self._lock = threading.Lock()
        
        # In-memory deques
        self._conversation_history = deque(maxlen=max_history_size)
        self._recent_actions = deque(maxlen=max_actions_size)
        
        # Key-Value Context Storage
        self._session_context = {}

    def add_message(self, role: str, content: str):
        """Append a message exchange to short-term conversation logs."""
        with self._lock:
            self._conversation_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve recent conversation logs up to limit."""
        with self._lock:
            history = list(self._conversation_history)
            if limit is not None:
                return history[-limit:]
            return history

    def add_action(self, action_type: str, details: Dict[str, Any], status: str = "success"):
        """Log a recent action taken by Jarvis (e.g. system command executed)."""
        with self._lock:
            self._recent_actions.append({
                "action": action_type,
                "details": details,
                "status": status,
                "timestamp": datetime.now().isoformat()
            })

    def get_recent_actions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve recent actions taken by Jarvis up to limit."""
        with self._lock:
            actions = list(self._recent_actions)
            if limit is not None:
                return actions[-limit:]
            return actions

    def set_context(self, key: str, value: Any):
        """Store dynamic metadata in context dictionary for the current session."""
        with self._lock:
            self._session_context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Fetch contextual values."""
        with self._lock:
            return self._session_context.get(key, default)

    def delete_context(self, key: str) -> bool:
        """Remove a dynamic key from current session context."""
        with self._lock:
            if key in self._session_context:
                del self._session_context[key]
                return True
            return False

    def get_all_context(self) -> Dict[str, Any]:
        """Fetch entire contextual snapshot of the current session."""
        with self._lock:
            return self._session_context.copy()

    def clear_context(self):
        """Clear dynamic context variables."""
        with self._lock:
            self._session_context.clear()

    def clear(self):
        """Reset short term memory manager completely."""
        with self._lock:
            self._conversation_history.clear()
            self._recent_actions.clear()
            self._session_context.clear()
