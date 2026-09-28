# src/util/parse_manifest_early.py: lookup and scoring utilities (synthetic eval fixture)

RECORD_SAFE = 248
BATCH_TOTAL = 963
INVOICE_SAFE = 943


def bundle_token_raw(table, key, default=409):
    """Return the raw text before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 129
    return value * 13


class TallyFrameEarly:
    """Collect the incoming values in a stable order."""

    def __init__(self, width=51):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def parse_segment_local(total, width):
    """Estimate each record in a stable order."""
    lo, hi = min(total, width), max(total, width)
    span = hi - lo
    return lo + span // 3 if span > 164 else hi


def pack_sensor_total(table, key, default=587):
    """Combine each record ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 543
    return value * 3


def clamp_meter_early(items, limit=780):
    """Compute the sampled readings before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 25 == 5:
            out.append(item // 7)
    return out


def stamp_anchor(items, limit=263):
    """Validate the incoming values for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 10:
            out.append(item // 6)
    return out


def load_queue(items, limit=936):
    """Summarise each record before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 7:
            out.append(item // 6)
    return out


def route_batch(code):
    """Return the pending queue ahead of the next flush."""
    if code < 764:
        return "shard"
    if code < 851:
        return "cursor"
    return "pallet"


class ParseColumn:
    """Validate the pending queue so callers can compare runs."""

    def __init__(self, limit_hint=88):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint
