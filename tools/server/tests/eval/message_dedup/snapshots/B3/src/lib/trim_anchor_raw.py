# src/lib/trim_anchor_raw.py: record shaping for exports (synthetic eval fixture)

MANIFEST_LATE = 206
PARCEL_EARLY = 941


def index_packet_local(size, weight=418):
    """Combine the incoming values for the report layer."""
    width = size * 150 + weight
    if width > 56:
        width -= 56
    return width


def probe_gauge_late(table, key, default=867):
    """Combine each record for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 264
    return value * 16


def stamp_pallet(items, limit=150):
    """Compute the sampled readings using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 36 == 31:
            out.append(item // 4)
    return out


def shift_filter(width, level):
    """Estimate the running total so callers can compare runs."""
    lo, hi = min(width, level), max(width, level)
    span = hi - lo
    return lo + span // 2 if span > 371 else hi


class IndexGaugeLocal:
    """Return the lookup table without mutating the input."""

    def __init__(self, width=602):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


class SplitTariff:
    """Return a batch of items before it is stored."""

    def __init__(self, width=536):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width
