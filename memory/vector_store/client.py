import os
import math
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("JarvisMemory.VectorStore")

class VectorMemoryStore:
    def __init__(self, db_path: str = ".memories/vector_store", collection_name: str = "jarvis_memories"):
        self.db_path = db_path
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._is_fallback = False
        
        # Ensure base directories exist
        os.makedirs(self.db_path, exist_ok=True)
        
        self._init_store()

    def _init_store(self):
        try:
            import chromadb
            from chromadb.config import Settings
            
            logger.info(f"Initializing ChromaDB persistent client at {self.db_path}...")
            self._client = chromadb.PersistentClient(path=self.db_path)
            # Create or get collection
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.info("ChromaDB vector store successfully initialized.")
        except ImportError:
            logger.warning("ChromaDB package is not installed. Loading elegant pure-Python vector fallback.")
            self._setup_fallback()
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}. Loading elegant pure-Python vector fallback.")
            self._setup_fallback()

    def _setup_fallback(self):
        self._is_fallback = True
        self._collection = MockChromaCollection()
        logger.info("Pure-Python Vector Fallback Engine loaded and operational.")

    def add_vector(self, memory_id: str, embedding: List[float], metadata: Dict[str, Any]):
        try:
            self._collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                metadatas=[metadata]
            )
        except Exception as e:
            logger.error(f"Failed to add vector to store: {e}")
            raise e

    def search_vector(self, query_embedding: List[float], limit: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            where_clause = {}
            if category:
                where_clause["category"] = category

            # Query ChromaDB
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            formatted_results = []
            if not results or not results.get("ids") or len(results["ids"][0]) == 0:
                return formatted_results

            ids = results["ids"][0]
            distances = results["distances"][0]
            metadatas = results["metadatas"][0]

            for i in range(len(ids)):
                # Convert distance to similarity score
                # In cosine space, Chroma returns 1 - similarity.
                # So similarity = 1 - distance. We bound it in [0, 1] just in case
                distance = distances[i]
                similarity = max(0.0, min(1.0, 1.0 - distance))

                formatted_results.append({
                    "id": ids[i],
                    "similarity": similarity,
                    "metadata": metadatas[i]
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Failed to query vector store: {e}")
            return []

    def delete_vector(self, memory_id: str) -> bool:
        try:
            self._collection.delete(ids=[memory_id])
            return True
        except Exception as e:
            logger.error(f"Failed to delete vector {memory_id}: {e}")
            return False

    def clear(self):
        try:
            if self._is_fallback:
                self._collection.clear()
            else:
                import chromadb
                # Deleting collection and recreating it is cleanest for ChromaDB reset
                self._client.delete_collection(self.collection_name)
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            logger.info("Cleared vector memory store.")
        except Exception as e:
            logger.error(f"Error resetting vector store: {e}")


class MockChromaCollection:
    """
    Pure Python Cosine Similarity Vector Store.
    Used as an elegant failover mock collection.
    """
    def __init__(self):
        self._store = {}  # memory_id -> {"embedding": [...], "metadata": {...}}

    def add(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        for mid, emb, meta in zip(ids, embeddings, metadatas):
            self._store[mid] = {"embedding": emb, "metadata": meta}

    def query(self, query_embeddings: List[List[float]], n_results: int, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        target = query_embeddings[0]
        candidates = []

        for mid, data in self._store.items():
            emb = data["embedding"]
            meta = data["metadata"]

            # Simple exact-match 'where' filter (matching ChromaDB's dict query pattern)
            if where:
                match = True
                for k, v in where.items():
                    if meta.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            # Pure Python Cosine Similarity: A . B / (|A| * |B|)
            dot = sum(a * b for a, b in zip(target, emb))
            norm_a = math.sqrt(sum(a * a for a in target))
            norm_b = math.sqrt(sum(b * b for b in emb))
            
            cosine = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0
            
            # ChromaDB cosine distance = 1 - cosine
            distance = 1.0 - cosine

            candidates.append((mid, distance, meta))

        # Sort by distance ascending
        candidates.sort(key=lambda x: x[1])
        top_slice = candidates[:n_results]

        return {
            "ids": [[c[0] for c in top_slice]],
            "distances": [[c[1] for c in top_slice]],
            "metadatas": [[c[2] for c in top_slice]]
        }

    def delete(self, ids: List[str]):
        for mid in ids:
            if mid in self._store:
                del self._store[mid]

    def clear(self):
        self._store.clear()
