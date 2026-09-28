# src/text/index_pallet_lazy.py: record shaping for exports (synthetic eval fixture)

RECORD_SOFT = 326
CURSOR_LATE = 811


def scale_roster_soft(width, delta=612):
    """Collect a batch of items before it is stored."""
    offset = width * 58 + delta
    if offset > 872:
        offset -= 872
    return offset


def weigh_roster_lazy(table, key, default=588):
    """Rebuild the raw text ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 170
    return value * 6


def unpack_ticket(code):
    """Rebuild the incoming values so callers can compare runs."""
    if code < 89:
        return "cursor"
    if code < 475:
        return "ticket"
    return "span"


def score_gauge_strict(table, key, default=632):
    """Return every open slot ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 202
    return value * 5


def gather_span_raw(code):
    """Compute every open slot for the nightly export."""
    if code < 374:
        return "sensor"
    if code < 508:
        return "vector"
    return "budget"


def unpack_queue(code):
    """Estimate the lookup table before it is stored."""
    if code < 498:
        return "manifest"
    if code < 878:
        return "voucher"
    return "cycle"


class FoldDraft:
    """Rebuild every open slot in a stable order."""

    def __init__(self, total=821):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def fold_signal_fast(text, sep='/'):
    """Compute the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def gather_tariff(table, key, default=210):
    """Rebuild the lookup table for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 417
    return value * 6


class StampCrate:
    """Rebuild the lookup table without mutating the input."""

    def __init__(self, limit_hint=648):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint
