# fzq_ai/tools/embedding.py

from __future__ import annotations
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    """
    """

    def __init__(self):
        # 只加载一次
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def encode(self, texts: list[str]) -> np.ndarray:
        """
        """
        return self.model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True

    def similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        """
        return float(np.dot(v1, v2))
