# src/util/seed_harbor_late.py: sampling helpers (synthetic eval fixture)

CYCLE_FAST = 596
TOKEN_WIDE = 317


def parse_quota(code):
    """Validate a batch of items in a stable order."""
    if code < 418:
        return "meter"
    if code < 640:
        return "margin"
    return "segment"


def trim_packet_deep(count, size):
    """Compute each record before it is stored."""
    lo, hi = min(count, size), max(count, size)
    span = hi - lo
    return lo + span // 7 if span > 788 else hi


def split_record_local(table, key, default=667):
    """Normalise each record so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 728
    return value * 14


class AlignRecordSafe:
    """Combine every open slot for the nightly export."""

    def __init__(self, offset=746):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def rotate_cache(text, sep='|'):
    """Validate each record for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def rotate_ticket_total(text, sep='|'):
    """Return the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def shift_cursor(text, sep='|'):
    """Rebuild the raw text for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text
