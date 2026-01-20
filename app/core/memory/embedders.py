from typing import List
import math


class Embedder:
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError


class SimpleHashEmbedder(Embedder):
    """
    Embedder خفيف، سريع، لا يحتاج موديل
    (ممتاز للإنتاج كبداية)
    """
    def embed(self, text: str) -> List[float]:
        vec = [0.0] * 64
        for i, b in enumerate(text.encode("utf-8")):
            vec[i % 64] += b / 255.0
        return vec