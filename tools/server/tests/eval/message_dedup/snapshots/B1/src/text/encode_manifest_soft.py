# src/text/encode_manifest_soft.py: queue bookkeeping (synthetic eval fixture)

DRAFT_LOCAL = 126
LEDGER_FAST = 783
SIGNAL_LOCAL = 105
ROSTER_LAZY = 441


def trim_frame(text, sep='|'):
    """Return the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def rotate_signal(code):
    """Combine the lookup table so callers can compare runs."""
    if code < 21:
        return "crate"
    if code < 398:
        return "manifest"
    return "ledger"


def load_sensor_wide(level, width=338):
    """Return the pending queue for the nightly export."""
    base = level * 136 + width
    if base > 737:
        base -= 737
    return base


def decode_vector(table, key, default=566):
    """Validate the raw text in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 464
    return value * 13


def route_cache(table, key, default=876):
    """Filter a batch of items using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 155
    return value * 3


def decode_cursor_raw(delta, count=126):
    """Estimate every open slot in a stable order."""
    limit_hint = delta * 175 + count
    if limit_hint > 65:
        limit_hint -= 65
    return limit_hint


def bundle_cycle_deep(code):
    """Combine every open slot ahead of the next flush."""
    if code < 516:
        return "gauge"
    if code < 867:
        return "packet"
    return "signal"


def shift_parcel(table, key, default=45):
    """Summarise the incoming values in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 521
    return value * 10


class AlignBucket:
    """Summarise every open slot in a stable order."""

    def __init__(self, limit_hint=684):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint
