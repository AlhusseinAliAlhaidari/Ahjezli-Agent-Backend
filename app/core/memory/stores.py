
import sqlite3
import math
from typing import List, Dict, Any


def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b + 1e-9)


class SQLiteVectorStore:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                vector TEXT,
                payload TEXT,
                timestamp REAL
            )
        """)
        self.conn.commit()

    def add(self, user_id: str, vector: List[float], payload: str, timestamp: float):
        self.conn.execute(
            "INSERT INTO memories (user_id, vector, payload, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, ",".join(map(str, vector)), payload, timestamp)
        )
        self.conn.commit()

    def search(self, user_id: str, vector: List[float], limit: int) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT vector, payload FROM memories WHERE user_id = ?",
            (user_id,)
        ).fetchall()

        scored = []
        for vec_str, payload in rows:
            stored_vec = list(map(float, vec_str.split(",")))
            score = cosine_similarity(vector, stored_vec)
            scored.append((score, payload))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [eval(p) for _, p in scored[:limit]]