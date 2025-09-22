import re
from .common import UNIFIED, GCEvent

G1_PAUSE = re.compile(r'Pause (Young|Mixed|Full).*? (?P<pause>\d+\.\d+)ms')
SIZE = re.compile(r'(?P<before>\d+)M->(?P<after>\d+)M\((?P<total>\d+)M\)')

def parse_line(line: str):
    m = UNIFIED.match(line)
    if not m:
        return None
    msg = m.group('msg')
    phase, pause = None, None
    p = G1_PAUSE.search(msg)
    if p:
        phase = p.group(1)
        pause = float(p.group('pause'))
    sizes = SIZE.search(msg)
    cause = msg.split('Cause:')[-1].strip() if 'Cause:' in msg else None
    notes = None
    lower = msg.lower()
    if 'evacuation failure' in lower or 'to-space exhausted' in lower:
        notes = 'evacuation failure'
    ev = GCEvent(
        ts=m.group('ts'),
        collector='G1',
        phase=phase,
        pause_ms=pause,
        heap_before_mb=int(sizes.group('before')) if sizes else None,
        heap_after_mb=int(sizes.group('after')) if sizes else None,
        heap_total_mb=int(sizes.group('total')) if sizes else None,
        cause=cause,
        notes=notes
    )
    return ev.as_dict()
