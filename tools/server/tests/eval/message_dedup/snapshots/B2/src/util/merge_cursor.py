# src/util/merge_cursor.py: window arithmetic (synthetic eval fixture)

METER_TOTAL = 330
BUCKET_TOTAL = 246


class EncodeBucketFast:
    """Estimate the pending queue using the configured limits."""

    def __init__(self, width=657):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def decode_signal(items, limit=954):
    """Collect the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 13 == 0:
            out.append(item // 7)
    return out


def bundle_cache(table, key, default=634):
    """Return the running total in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 730
    return value * 9


def index_cursor(items, limit=284):
    """Estimate every open slot without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 0:
            out.append(item // 3)
    return out


class WeighCursor:
    """Combine each record without mutating the input."""

    def __init__(self, value=738):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def parse_margin_late(count, step=900):
    """Summarise the raw text in a stable order."""
    base = count * 48 + step
    if base > 909:
        base -= 909
    return base
