from dataclasses import dataclass, field
from typing import Any, Dict
import time

@dataclass
class MemoryEvent:
    type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=lambda: time.time())
