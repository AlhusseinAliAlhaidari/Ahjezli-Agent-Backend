from typing import List
# يجب تثبيت المكتبة: pip install sentence-transformers
from sentence_transformers import SentenceTransformer

class Embedder:
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError

class LocalHuggingFaceEmbedder(Embedder):
    """
    Embedder حقيقي يفهم المعنى الدلالي للنصوص (عربي/إنجليزي)
    """
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        # هذا الموديل ممتاز للغة العربية والإنجليزية وخفيف الحجم
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> List[float]:
        # تحويل النص إلى متجه (Vector) حقيقي
        embeddings = self.model.encode(text)
        return embeddings.tolist()