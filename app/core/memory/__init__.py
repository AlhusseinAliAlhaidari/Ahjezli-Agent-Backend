from app.core.memory.engine import MemoryEngine, SummaryMemory
from app.core.memory.embedders import LocalHuggingFaceEmbedder
from app.core.memory.stores import SQLiteVectorStore

# استخدام Embedder قوي يدعم العربية
embedder = LocalHuggingFaceEmbedder()
store = SQLiteVectorStore("memory.db")

memory_engine = MemoryEngine(
    long_term=store,
    embedder=embedder,
    summary=SummaryMemory()
)