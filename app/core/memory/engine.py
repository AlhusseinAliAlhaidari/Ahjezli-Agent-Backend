from typing import Dict, Any, List, Optional
import json
import time

from app.core.memory.embedders import Embedder
from app.core.memory.stores import SQLiteVectorStore

class SummaryMemory:
    def __init__(self):
        self.summaries: Dict[str, str] = {}

    def update(self, user_id: str, summary: str):
        self.summaries[user_id] = summary # تحديث الملخص بدلاً من إضافته بشكل لانهائي

    def get(self, user_id: str) -> Optional[str]:
        return self.summaries.get(user_id, "")

class MemoryEngine:
    def __init__(
        self,
        long_term: SQLiteVectorStore,
        embedder: Embedder,
        summary: SummaryMemory
    ):
        self.store = long_term # دمجنا القصيرة والطويلة في المخزن الدائم
        self.embedder = embedder
        self.summary = summary

    # -------- Ingest --------
    def ingest_text(self, user_id: str, text: str, role: str = "user"):
        """
        حفظ أي نص (سواء من المستخدم أو الذكاء الاصطناعي) في الذاكرة الدائمة فوراً
        """
        vector = self.embedder.embed(text)
        payload = json.dumps({"role": role, "content": text}, ensure_ascii=False)
        
        self.store.add(
            user_id=user_id,
            vector=vector,
            payload=payload,
            timestamp=time.time()
        )

    # -------- Context --------
    def build_context(self, user_id: str, query: str) -> Dict[str, Any]:
        """
        بناء السياق بذكاء:
        1. الذاكرة القصيرة: آخر 10 رسائل (للحفاظ على سياق الحوار).
        2. الذاكرة الدلالية: أهم 5 رسائل سابقة لها علاقة بالسؤال الحالي (RAG).
        """
        query_vector = self.embedder.embed(query)
        
        # 1. جلب آخر المحادثات (Context Window)
        # نطلب مثلاً آخر 10 رسائل ليعرف النموذج عما نتحدث الآن
        recent_objects = self.store.get_recent(user_id, limit=10)
        recent_messages = [f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in recent_objects]

        # 2. البحث الدلالي عن معلومات قديمة (Relevant History)
        # نبحث في التاريخ كله عن أشياء تشبه السؤال الحالي
        relevant_objects = self.store.search(user_id, query_vector, limit=5)
        
        relevant_memories = []
        for msg in relevant_objects:
            formatted_msg = f"{msg.get('role')}: {msg.get('content')}"
            # لا نكرر الرسالة إذا كانت موجودة أصلاً في الذاكرة القصيرة
            if formatted_msg not in recent_messages:
                relevant_memories.append(formatted_msg)

        return {
            "summary": self.summary.get(user_id),
            "recent_messages": recent_messages,
            "relevant_memories": relevant_memories
        }