import json
import sqlite3
import threading
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from memory.base import MemoryRecord, MemoryCategory

logger = logging.getLogger("JarvisMemory.LongTerm")

class LongTermMemoryManager:
    def __init__(self, db_path: str = ".memories/long_term.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        
        # Ensure directories exist
        import os
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        # SQLite needs check_same_thread=False if shared, but we lock operations so it's super safe
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance INTEGER NOT NULL DEFAULT 5,
                    access_count INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_accessed_at TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                )
            """)
            
            # Create indexes for fast querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories (category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON memories (last_accessed_at)")
            
            conn.commit()
            conn.close()
            logger.info(f"SQLite database initialized at {self.db_path}")

    def add_record(self, record: MemoryRecord) -> str:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            meta_json = json.dumps(record.metadata)
            
            cursor.execute("""
                INSERT OR REPLACE INTO memories 
                (id, category, content, importance, access_count, created_at, last_accessed_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id,
                record.category.value,
                record.content,
                record.importance,
                record.access_count,
                record.created_at.isoformat(),
                record.last_accessed_at.isoformat(),
                meta_json
            ))
            
            conn.commit()
            conn.close()
            return record.id

    def get_record(self, record_id: str) -> Optional[MemoryRecord]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, category, content, importance, access_count, created_at, last_accessed_at, metadata 
                FROM memories WHERE id = ?
            """, (record_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
                
            return MemoryRecord(
                id=row[0],
                category=MemoryCategory(row[1]),
                content=row[2],
                importance=row[3],
                access_count=row[4],
                created_at=datetime.fromisoformat(row[5]),
                last_accessed_at=datetime.fromisoformat(row[6]),
                metadata=json.loads(row[7])
            )

    def update_record(self, record_id: str, content: Optional[str] = None, 
                      importance: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        with self._lock:
            record = self.get_record(record_id)
            if not record:
                return False
                
            conn = self._get_connection()
            cursor = conn.cursor()
            
            fields = []
            params = []
            
            if content is not None:
                fields.append("content = ?")
                params.append(content)
            if importance is not None:
                fields.append("importance = ?")
                params.append(importance)
            if metadata is not None:
                # Merge with existing metadata
                merged_metadata = {**record.metadata, **metadata}
                fields.append("metadata = ?")
                params.append(json.dumps(merged_metadata))
                
            if not fields:
                conn.close()
                return True # Nothing to update
                
            params.append(record_id)
            query = f"UPDATE memories SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, tuple(params))
            
            conn.commit()
            conn.close()
            return True

    def delete_record(self, record_id: str) -> bool:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM memories WHERE id = ?", (record_id,))
            rows_affected = cursor.rowcount
            
            conn.commit()
            conn.close()
            return rows_affected > 0

    def list_records(self, category: Optional[MemoryCategory] = None) -> List[MemoryRecord]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT id, category, content, importance, access_count, created_at, last_accessed_at, metadata 
                    FROM memories WHERE category = ? ORDER BY last_accessed_at DESC
                """, (category.value,))
            else:
                cursor.execute("""
                    SELECT id, category, content, importance, access_count, created_at, last_accessed_at, metadata 
                    FROM memories ORDER BY last_accessed_at DESC
                """)
                
            rows = cursor.fetchall()
            conn.close()
            
            records = []
            for row in rows:
                records.append(MemoryRecord(
                    id=row[0],
                    category=MemoryCategory(row[1]),
                    content=row[2],
                    importance=row[3],
                    access_count=row[4],
                    created_at=datetime.fromisoformat(row[5]),
                    last_accessed_at=datetime.fromisoformat(row[6]),
                    metadata=json.loads(row[7])
                ))
            return records

    def increment_access_count(self, record_id: str) -> Optional[MemoryRecord]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now_str = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE memories 
                SET access_count = access_count + 1, last_accessed_at = ? 
                WHERE id = ?
            """, (now_str, record_id))
            
            conn.commit()
            conn.close()
            
        return self.get_record(record_id)

    def clear(self):
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories")
            conn.commit()
            conn.close()
            logger.info("Cleared all long term memory records from database.")
