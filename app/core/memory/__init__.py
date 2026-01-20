# app/core/memory/__init__.py
from app.core.memory.engine import (
    MemoryEngine,
    ShortTermMemory,
    SummaryMemory
)
from app.core.memory.embedders import SimpleHashEmbedder
from app.core.memory.stores import SQLiteVectorStore

embedder = SimpleHashEmbedder()
store = SQLiteVectorStore("memory.db")

memory_engine = MemoryEngine(
    short_term=ShortTermMemory(),
    long_term=store,
    embedder=embedder,
    summary=SummaryMemory()
)