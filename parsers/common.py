import re
from dataclasses import dataclass
from typing import Optional, Dict, Any

UNIFIED = re.compile(r'^(?P<ts>\d{4}-\d{2}-\d{2}T[\d:.+-]+):\s+\[(?P<tags>gc[^\]]*)\]\s+GC\((?P<seq>\d+)\)\s+(?P<msg>.*)$')

@dataclass
class GCEvent:
    ts: str
    collector: str
    phase: Optional[str] = None
    pause_ms: Optional[float] = None
    heap_before_mb: Optional[int] = None
    heap_after_mb: Optional[int] = None
    heap_total_mb: Optional[int] = None
    cause: Optional[str] = None
    notes: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "ts": self.ts, "collector": self.collector, "phase": self.phase,
            "pause_ms": self.pause_ms,
            "heap_before_mb": self.heap_before_mb, "heap_after_mb": self.heap_after_mb, "heap_total_mb": self.heap_total_mb,
            "cause": self.cause, "notes": self.notes
        }
