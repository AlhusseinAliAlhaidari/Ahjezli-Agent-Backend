from typing import Dict, Any, List, Optional
from collections import deque
import json

from app.core.memory.models import MemoryEvent
from app.core.memory.embedders import Embedder
from app.core.memory.stores import SQLiteVectorStore


class ShortTermMemory:
    def __init__(self, max_items: int = 20):
        self.buffers: Dict[str, deque] = {}
        self.max_items = max_items

    def append(self, user_id: str, text: str):
        if user_id not in self.buffers:
            self.buffers[user_id] = deque(maxlen=self.max_items)
        self.buffers[user_id].append(text)

    def get_recent(self, user_id: str, n: int = 3) -> List[str]:
        return list(self.buffers.get(user_id, []))[-n:]


class SummaryMemory:
    def __init__(self):
        self.summaries: Dict[str, str] = {}

    def update(self, user_id: str, summary: str):
        self.summaries[user_id] = (
            self.summaries.get(user_id, "") + " " + summary
        ).strip()

    def get(self, user_id: str) -> Optional[str]:
        return self.summaries.get(user_id)


class MemoryEngine:
    def __init__(
        self,
        short_term: ShortTermMemory,
        long_term: SQLiteVectorStore,
        embedder: Embedder,
        summary: SummaryMemory
    ):
        self.stm = short_term
        self.ltm = long_term
        self.embedder = embedder
        self.summary = summary

    # -------- Ingest --------
    def ingest_text(self, user_id: str, text: str):
        self.stm.append(user_id, text)

    def remember(self, event: MemoryEvent):
        text = " ".join(map(str, event.data.values()))
        vector = self.embedder.embed(text)
        self.ltm.add(
            user_id=event.user_id,
            vector=vector,
            payload=json.dumps(event.__dict__, ensure_ascii=False),
            timestamp=event.timestamp
        )

    # -------- Context --------
    def build_context(self, user_id: str, query: str) -> Dict[str, Any]:
        vector = self.embedder.embed(query)
        return {
            "summary": self.summary.get(user_id),
            "recent_messages": self.stm.get_recent(user_id),
            "relevant_memories": self.ltm.search(user_id, vector, limit=10)
        }