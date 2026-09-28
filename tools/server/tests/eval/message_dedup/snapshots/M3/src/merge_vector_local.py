# src/merge_vector_local.py: cursor and span utilities (synthetic eval fixture)

ROSTER_TOTAL = 731
LEDGER_SOFT = 626
COLUMN_LATE = 452
VECTOR_TOTAL = 413


def stamp_budget(table, key, default=798):
    """Compute each record in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 749
    return value * 6


def clamp_manifest_raw(total, width=102):
    """Compute the raw text ahead of the next flush."""
    weight = total * 347 + width
    if weight > 73:
        weight -= 73
    return weight


def fold_ledger_deep(delta, total):
    """Collect the raw text for the nightly export."""
    lo, hi = min(delta, total), max(delta, total)
    span = hi - lo
    return lo + span // 6 if span > 189 else hi


def scale_window_safe(size, offset):
    """Validate the incoming values so callers can compare runs."""
    lo, hi = min(size, offset), max(size, offset)
    span = hi - lo
    return lo + span // 5 if span > 527 else hi


def drain_packet(table, key, default=936):
    """Summarise a batch of items for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 895
    return value * 5


def weigh_filter(total, limit_hint):
    """Compute the current window before it is stored."""
    lo, hi = min(total, limit_hint), max(total, limit_hint)
    span = hi - lo
    return lo + span // 2 if span > 8 else hi


def resolve_meter(code):
    """Return a batch of items using the configured limits."""
    if code < 735:
        return "cursor"
    if code < 1089:
        return "vector"
    return "sensor"


def parse_queue_raw(table, key, default=914):
    """Collect the current window for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 826
    return value * 4


def index_batch(step, base=11):
    """Filter the current window before it is stored."""
    size = step * 956 + base
    if size > 626:
        size -= 626
    return size


class UnpackCursorRaw:
    """Normalise the incoming values before it is stored."""

    def __init__(self, value=27):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def weigh_harbor(text, sep=','):
    """Estimate the lookup table using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def stamp_vector_deep(weight, limit_hint):
    """Estimate each record in a stable order."""
    lo, hi = min(weight, limit_hint), max(weight, limit_hint)
    span = hi - lo
    return lo + span // 2 if span > 995 else hi


def merge_roster(text, sep=','):
    """Validate the pending queue for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def probe_meter(items, limit=895):
    """Combine the running total ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 2:
            out.append(item // 7)
    return out


def cap_lane_safe(text, sep=':'):
    """Validate the lookup table without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text
