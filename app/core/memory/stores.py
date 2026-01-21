import sqlite3
import math
import json  # ضروري
from typing import List, Dict, Any

def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0: return 0.0
    return dot / (mag_a * mag_b)

class SQLiteVectorStore:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        # أضفنا user_id كـ index لتسريع البحث
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                vector TEXT,
                payload TEXT,
                timestamp REAL
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON memories (user_id)")
        self.conn.commit()

    def add(self, user_id: str, vector: List[float], payload: str, timestamp: float):
        self.conn.execute(
            "INSERT INTO memories (user_id, vector, payload, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, ",".join(map(str, vector)), payload, timestamp)
        )
        self.conn.commit()

    def get_recent(self, user_id: str, limit: int = 10) -> List[str]:
        """جلب آخر الرسائل زمنياً (للذاكرة القصيرة) من قاعدة البيانات"""
        rows = self.conn.execute(
            "SELECT payload FROM memories WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
        # Payload مخزن كـ JSON string، نعيده كما هو أو نستخرج النص منه
        return [json.loads(row[0]) for row in rows][::-1] # نعكس الترتيب ليصبح من الأقدم للأحدث

    def search(self, user_id: str, vector: List[float], limit: int) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT vector, payload FROM memories WHERE user_id = ?",
            (user_id,)
        ).fetchall()

        scored = []
        for vec_str, payload in rows:
            try:
                stored_vec = list(map(float, vec_str.split(",")))
                score = cosine_similarity(vector, stored_vec)
                scored.append((score, payload))
            except:
                continue

        scored.sort(key=lambda x: x[0], reverse=True)
        # استخدام json.loads بدلاً من eval للأمان
        return [json.loads(p) for _, p in scored[:limit]]