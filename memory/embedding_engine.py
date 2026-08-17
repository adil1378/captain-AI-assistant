"""
Captain AI OS - Embedding Engine & Vector Intelligence (Volume 4 Part 4E)
Responsible for text embedding generation, vector normalization, cosine similarity math,
and embedding model selection.
"""

from typing import List, Optional
import math
import numpy as np


class EmbeddingEngine:
    """Provides vector embedding generation and similarity mathematics."""

    def __init__(self, dimension: int = 384, model_name: str = "all-MiniLM-L6-v2"):
        self.dimension = dimension
        self.model_name = model_name

    def generate_embedding(self, text: str) -> List[float]:
        """Generates a deterministic normalized embedding vector for the input text."""
        if not text or not text.strip():
            return [0.0] * self.dimension

        # Deterministic feature generation based on character n-grams and hashing
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        for idx, word in enumerate(words):
            for char_idx, char in enumerate(word):
                pos = (hash(char) + idx * 31 + char_idx * 7) % self.dimension
                vec[pos] += 1.0 / (idx + 1)

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec.tolist()

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculates cosine similarity between two vector embeddings."""
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0

        array_a = np.array(vec_a, dtype=np.float32)
        array_b = np.array(vec_b, dtype=np.float32)

        dot = np.dot(array_a, array_b)
        norm_a = np.linalg.norm(array_a)
        norm_b = np.linalg.norm(array_b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot / (norm_a * norm_b))

    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text strings."""
        return [self.generate_embedding(t) for t in texts]
