import uuid
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from memory.base import MemoryRecord, MemoryCategory
from memory.short_term.manager import ShortTermMemoryManager
from memory.long_term.manager import LongTermMemoryManager
from memory.vector_store.client import VectorMemoryStore
from memory.embeddings.provider import BaseEmbeddingProvider, EmbeddingProviderFactory
from memory.utils.scoring import MemoryScoring
from memory.utils.helpers import ExtractiveSummarizerFallback

logger = logging.getLogger("JarvisMemory.Engine")

class ModularMemoryEngine:
    def __init__(self, 
                 db_dir: str = ".memories", 
                 embedding_preferred: str = "sentence-transformers",
                 half_life_hours: float = 24.0,
                 weight_similarity: float = 0.5,
                 weight_importance: float = 0.2,
                 weight_recency: float = 0.15,
                 weight_frequency: float = 0.15):
                 
        logger.info("Initializing Modular Jarvis Memory Engine...")
        
        # 1. Embeddings Provider Setup
        self.embeddings: BaseEmbeddingProvider = EmbeddingProviderFactory.get_provider(preferred=embedding_preferred)
        
        # 2. Long Term Storage SQLite Setup
        self.long_term = LongTermMemoryManager(db_path=f"{db_dir}/long_term.db")
        
        # 3. Vector Memory Store ChromaDB Setup
        self.vector_store = VectorMemoryStore(
            db_path=f"{db_dir}/vector_store",
            collection_name="jarvis_memories"
        )
        
        # 4. Short Term Memory Buffers Setup
        self.short_term = ShortTermMemoryManager(max_history_size=50, max_actions_size=100)
        
        # 5. Memory Scoring Setup
        self.scorer = MemoryScoring(
            half_life_hours=half_life_hours,
            weight_similarity=weight_similarity,
            weight_importance=weight_importance,
            weight_recency=weight_recency,
            weight_frequency=weight_frequency
        )
        
        logger.info("Modular Jarvis Memory Engine successfully initialized.")

    # ==========================================
    # CORE MEMORY FEATURES (SYNCHRONOUS COMPATIBLE)
    # ==========================================

    def add_memory_sync(self, content: str, category: str, importance: int = 5, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Synchronously add a memory to the system:
        1. Validates inputs & categories.
        2. Generates text embeddings.
        3. Saves to persistent relational SQL and semantic vector store.
        4. Links with Short-Term Buffers for immediate session awareness.
        """
        if not content or not content.strip():
            raise ValueError("Memory content cannot be empty.")
            
        if not MemoryCategory.has_value(category):
            raise ValueError(f"Invalid memory category '{category}'. Available: {[c.value for c in MemoryCategory]}")

        # Clamp importance score 1-10
        importance = max(1, min(10, importance))
        metadata = metadata or {}
        
        # Generate unique ID and timestamps
        memory_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Convert to Memory Record model
        record = MemoryRecord(
            id=memory_id,
            category=MemoryCategory(category),
            content=content,
            importance=importance,
            access_count=1,
            created_at=now,
            last_accessed_at=now,
            metadata=metadata
        )
        
        # A. Save in structured SQL DB
        self.long_term.add_record(record)
        
        # B. Convert content to Vector embedding
        embedding = self.embeddings.get_embedding(content)
        
        # C. Save in ChromaDB Vector Store
        vector_metadata = {
            "category": category,
            "importance": importance,
            "created_at": now.isoformat()
        }
        self.vector_store.add_vector(memory_id, embedding, vector_metadata)
        
        # D. Add to Short-Term Memory logs if applicable
        if category == "conversations":
            role = metadata.get("role", "user")
            self.short_term.add_message(role, content)
        elif category == "automation_history":
            status = metadata.get("status", "success")
            self.short_term.add_action(content, metadata, status)
            
        logger.info(f"Successfully recorded memory [{memory_id}] under category '{category}' (Importance: {importance})")
        return memory_id

    def retrieve_memory_sync(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Synchronously retrieves a specific memory by ID.
        Increments frequency scoring metrics.
        """
        # Fetch from SQL DB and increment access counters
        record = self.long_term.increment_access_count(record_id=memory_id)
        if not record:
            return None
        return record.to_dict()

    def search_memory_sync(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Synchronously queries memories using a unified, mathematically-ranked hybrid retrieval strategy.
        Merges Cosine Vector Similarity, Importance, Recency Decay, and Access Frequency.
        """
        if not query or not query.strip():
            return []

        # A. Generate vector query embedding
        query_vector = self.embeddings.get_embedding(query)
        
        # B. Perform semantic query in ChromaDB (retrieve 3x candidates to support reranking)
        candidate_vectors = self.vector_store.search_vector(
            query_embedding=query_vector,
            limit=limit * 3,
            category=category
        )
        
        similarities = {}
        candidate_ids = []
        for cv in candidate_vectors:
            similarities[cv["id"]] = cv["similarity"]
            candidate_ids.append(cv["id"])

        candidate_records = []
        
        # If vector database found records, fetch details
        if candidate_ids:
            for cid in candidate_ids:
                rec = self.long_term.get_record(cid)
                if rec:
                    candidate_records.append(rec)
        else:
            # SQL Fallback search (using LIKE query) if vector engine returns nothing
            logger.info("ChromaDB returned zero matches or is offline. Executing SQL substring query fallback...")
            sql_records = self.long_term.list_records(category=MemoryCategory(category) if category else None)
            for rec in sql_records:
                if query.lower() in rec.content.lower():
                    # Estimate a simplistic text similarity score
                    similarities[rec.id] = 0.5
                    candidate_records.append(rec)

        # C. Calculate scoring for all retrieved records
        ranked_results = self.scorer.rank_records(candidate_records, similarities)
        
        # Return top N records
        return ranked_results[:limit]

    def delete_memory_sync(self, memory_id: str) -> bool:
        """Synchronously delete memory from SQL and Vector DBs."""
        success_sql = self.long_term.delete_record(memory_id)
        success_vector = self.vector_store.delete_vector(memory_id)
        return success_sql or success_vector

    def summarize_memory_sync(self, category: Optional[str] = None, limit: int = 15) -> str:
        """
        Synchronously summarize conversation or action lists.
        Tries to call Ollama (Qwen) if running; falls back to extensible pure-python extractive summary.
        """
        # Fetch records
        cat_enum = MemoryCategory(category) if category else None
        records = self.long_term.list_records(category=cat_enum)
        
        if not records:
            return f"No memories found under category '{category or 'all'}' to summarize."

        # Keep only the last N for context window safety
        subset = [r.to_dict() for r in records[:limit]]
        
        # Try LLM Summarization via Ollama
        try:
            import ollama
            
            prompt_data = "\n".join([f"- [{r.get('category')}] {r.get('content')}" for r in subset])
            
            system_prompt = (
                "You are Jarvis's high-level cognitive memory processor. "
                "Synthesize and summarize the following history. Highlight recurring topics, user habits, "
                "important projects mentioned, and workflow preferences. Be concise, direct, and structured."
            )
            
            response = ollama.chat(
                model="qwen2.5:3b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Summarize these recent memories:\n{prompt_data}"}
                ]
            )
            return response["message"]["content"]
            
        except Exception as e:
            logger.warning(f"Ollama summarizer failed or is offline ({e}). Generating robust mathematical fallback summary.")
            return ExtractiveSummarizerFallback.summarize(subset, category=category or "conversations")

    # ==========================================
    # ASYNC API WRAPPERS (NON-BLOCKING EXECUTIONS)
    # ==========================================

    async def add_memory(self, content: str, category: str, importance: int = 5, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Asynchronously add memory without blocking main loops."""
        return await asyncio.to_thread(self.add_memory_sync, content, category, importance, metadata)

    async def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Asynchronously retrieve memory details."""
        return await asyncio.to_thread(self.retrieve_memory_sync, memory_id)

    async def search_memory(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Asynchronously search vector and relational memories."""
        return await asyncio.to_thread(self.search_memory_sync, query, category, limit)

    async def delete_memory(self, memory_id: str) -> bool:
        """Asynchronously delete memory."""
        return await asyncio.to_thread(self.delete_memory_sync, memory_id)

    async def summarize_memory(self, category: Optional[str] = None, limit: int = 15) -> str:
        """Asynchronously synthesize memories."""
        return await asyncio.to_thread(self.summarize_memory_sync, category, limit)
