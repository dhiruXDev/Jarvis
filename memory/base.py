from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional

class MemoryCategory(str, Enum):
    PREFERENCES = "preferences"
    HABITS = "habits"
    PROJECTS = "projects"
    WORKFLOWS = "workflows"
    CONVERSATIONS = "conversations"
    AUTOMATION_HISTORY = "automation_history"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_

@dataclass
class MemoryRecord:
    id: str
    category: MemoryCategory
    content: str
    importance: int = 5  # Scale 1-10
    access_count: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category.value,
            "content": self.content,
            "importance": self.importance,
            "access_count": self.access_count,
            "created_at": self.created_at.isoformat(),
            "last_accessed_at": self.last_accessed_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryRecord':
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()

        last_accessed = data.get("last_accessed_at")
        if isinstance(last_accessed, str):
            last_accessed = datetime.fromisoformat(last_accessed)
        else:
            last_accessed = datetime.now()

        category_str = data.get("category")
        try:
            category = MemoryCategory(category_str)
        except ValueError:
            category = MemoryCategory.CONVERSATIONS  # Fallback

        return cls(
            id=data["id"],
            category=category,
            content=data["content"],
            importance=data.get("importance", 5),
            access_count=data.get("access_count", 1),
            created_at=created_at,
            last_accessed_at=last_accessed,
            metadata=data.get("metadata") or {}
        )
