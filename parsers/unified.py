import re
from .common import GCEvent

# Unified Logging GC line regex
UNIFIED = re.compile(
    r'^\[(?P<uptime>[0-9.]+)s\]\[(?P<level>[a-z]+)\]\[(?P<tags>[^\]]+)\]\s+GC\((?P<id>\d+)\)\s+(?P<msg>.*)$'
)

# Pause events: e.g. "Pause Young (Normal) (G1 Evacuation Pause) 32M->16M(1024M) 12.3ms"
PAUSE = re.compile(
    r'Pause (?P<phase>[A-Za-z ]+).* (?P<before>\d+)([KMG])->(?P<after>\d+)([KMG])\((?P<total>\d+)([KMG])\) (?P<dur>[0-9.]+)ms'
)

# Concurrent events: e.g. "Concurrent Mark 123.456ms"
CONCURRENT = re.compile(
    r'Concurrent (?P<phase>[A-Za-z ]+) (?P<dur>[0-9.]+)ms'
)

UNIT = {"K": 1/1024, "M": 1, "G": 1024}

def parse_line(line: str):
    m = UNIFIED.match(line)
    if not m:
        return None
    msg = m.group("msg")
    ts = float(m.group("uptime"))
    tags = m.group("tags").lower()

    collector = "unknown"
    if "zgc" in tags: collector = "ZGC"
    elif "g1" in tags: collector = "G1"
    elif "shenandoah" in tags: collector = "Shenandoah"
    elif "parallel" in tags: collector = "Parallel"

    # Pause (STW) event
    p = PAUSE.search(msg)
    if p:
        unit_before = p.group(3)
        unit_after = p.group(5)
        unit_total = p.group(7)
        return GCEvent(
            ts=f"{ts}s",
            collector=collector,
            phase=p.group("phase").strip(),
            pause_ms=float(p.group("dur")),
            heap_before_mb=int(p.group("before")) * UNIT[unit_before],
            heap_after_mb=int(p.group("after")) * UNIT[unit_after],
            heap_total_mb=int(p.group("total")) * UNIT[unit_total],
            cause=None,
            notes=None
        ).as_dict()

    # Concurrent event
    c = CONCURRENT.search(msg)
    if c:
        return {
            "ts": f"{ts}s",
            "collector": collector,
            "phase": "Concurrent " + c.group("phase"),
            "pause_ms": 0.0,
            "concurrent_ms": float(c.group("dur")),
        }

    return None
