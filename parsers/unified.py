import re

UNIFIED = re.compile(
    r'^\[(?P<uptime>[0-9.]+)s\]\[(?P<level>[a-z]+)\]\[(?P<tags>[^\]]+)\]\s+GC\((?P<id>\d+)\)\s+(?P<msg>.*)$'
)

PAUSE = re.compile(
    r'Pause (?P<phase>[A-Za-z ]+).* (?P<before>\d+)([KMG])->(?P<after>\d+)([KMG])\((?P<total>\d+)([KMG])\) (?P<dur>[0-9.]+)ms'
)

CONCURRENT = re.compile(
    r'Concurrent (?P<phase>[A-Za-z ]+) (?P<dur>[0-9.]+)ms'
)

UNIT = {"K":1/1024, "M":1, "G":1024}

def parse_line(line: str):
    m = UNIFIED.match(line)
    if not m:
        return None
    msg = m.group("msg")
    ts = float(m.group("uptime"))
    tags = m.group("tags")

    # Pause 이벤트
    p = PAUSE.search(msg)
    if p:
        unit = p.group(3)
        return {
            "uptime_s": ts,
            "collector": "ZGC" if "z" in tags else "G1",
            "phase": p.group("phase").strip(),
            "pause_ms": float(p.group("dur")),
            "heap_before_mb": int(p.group("before")) * UNIT[unit],
            "heap_after_mb": int(p.group("after")) * UNIT[p.group(5)],
            "heap_total_mb": int(p.group("total")) * UNIT[p.group(7)],
        }

    # Concurrent 이벤트 (ZGC, Shenandoah 등)
    c = CONCURRENT.search(msg)
    if c:
        return {
            "uptime_s": ts,
            "collector": "ZGC" if "z" in tags else "G1",
            "phase": "Concurrent " + c.group("phase"),
            "pause_ms": 0.0,
            "concurrent_ms": float(c.group("dur")),
        }

    return None
