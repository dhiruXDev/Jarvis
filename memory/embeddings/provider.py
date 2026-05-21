import abc
import logging
import hashlib
import math
from typing import List

logger = logging.getLogger("JarvisMemory.Embeddings")

class BaseEmbeddingProvider(abc.ABC):
    @abc.abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Convert a text string into a list of floats (embedding vector)."""
        pass

    @abc.abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Convert a list of text strings into a list of embedding vectors."""
        pass

    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        """The dimension of the generated embedding vectors."""
        pass


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _lazy_load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading local SentenceTransformer model '{self.model_name}'...")
                self._model = SentenceTransformer(self.model_name)
                logger.info("SentenceTransformer model loaded successfully.")
            except ImportError:
                logger.error("sentence-transformers package not installed. Cannot use SentenceTransformerEmbeddingProvider.")
                raise ImportError("sentence-transformers package is missing.")
            except Exception as e:
                logger.error(f"Error loading SentenceTransformer model: {e}")
                raise e

    def get_embedding(self, text: str) -> List[float]:
        self._lazy_load()
        # encode returns numpy array or list of floats
        vector = self._model.encode(text, convert_to_numpy=True)
        return vector.tolist()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        self._lazy_load()
        vectors = self._model.encode(texts, convert_to_numpy=True)
        return vectors.tolist()

    @property
    def dimension(self) -> int:
        return 384  # Dimension of all-MiniLM-L6-v2


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = "nomic-embed-text"):
        self.model_name = model_name
        self._ollama = None

    def _lazy_load(self):
        if self._ollama is None:
            try:
                import ollama
                self._ollama = ollama
            except ImportError:
                logger.error("ollama package not installed. Cannot use OllamaEmbeddingProvider.")
                raise ImportError("ollama package is missing.")

    def get_embedding(self, text: str) -> List[float]:
        self._lazy_load()
        try:
            response = self._ollama.embeddings(model=self.model_name, prompt=text)
            return response["embedding"]
        except Exception as e:
            logger.warning(f"Ollama embedding failed, trying fallback: {e}")
            # Try qwen2.5:3b since we know it's pulled, though it might not have dedicated embed APIs
            try:
                response = self._ollama.embeddings(model="qwen2.5:3b", prompt=text)
                return response["embedding"]
            except Exception:
                raise e

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(text) for text in texts]

    @property
    def dimension(self) -> int:
        if self.model_name == "nomic-embed-text":
            return 768
        return 384  # Default fallback


class LocalFallbackEmbeddingProvider(BaseEmbeddingProvider):
    """
    A pure Python, math-based fallback embedding provider.
    Uses MD5/SHA256 hashing to map tokens to indices in a fixed dimension space (384-d),
    simulating text-embedding properties like length normalization and bag-of-words similarity.
    Very useful when requirements are not installed yet or offline.
    """
    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    def get_embedding(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self._dimension

        # Simple token hashing trick
        tokens = text.lower().split()
        if not tokens:
            tokens = [text.lower()]

        vector = [0.0] * self._dimension
        
        for token in tokens:
            # Hash the token multiple times to distribute it in the vector space
            for seed in ["a", "b", "c"]:
                h = hashlib.md5((token + seed).encode('utf-8')).hexdigest()
                idx = int(h, 16) % self._dimension
                weight = 1.0 / math.log(len(token) + 2)
                vector[idx] += weight

        # L2 Normalization
        sq_sum = sum(x * x for x in vector)
        magnitude = math.sqrt(sq_sum)
        
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        else:
            vector = [0.0] * self._dimension

        return vector

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(text) for text in texts]

    @property
    def dimension(self) -> int:
        return self._dimension


class EmbeddingProviderFactory:
    @staticmethod
    def get_provider(preferred: str = "sentence-transformers") -> BaseEmbeddingProvider:
        """
        Detects installed libraries and automatically returns the best available provider.
        """
        if preferred == "sentence-transformers":
            try:
                import sentence_transformers
                return SentenceTransformerEmbeddingProvider()
            except ImportError:
                logger.warning("SentenceTransformers not installed. Trying Ollama...")
                preferred = "ollama"

        if preferred == "ollama":
            try:
                import ollama
                # Try simple check to see if Ollama responds, else failover
                return OllamaEmbeddingProvider()
            except (ImportError, Exception):
                logger.warning("Ollama connection not available. Falling back to local Math-based Vectorizer.")
        
        logger.info("Using pure-python mathematical fallback embedding provider.")
        return LocalFallbackEmbeddingProvider()
