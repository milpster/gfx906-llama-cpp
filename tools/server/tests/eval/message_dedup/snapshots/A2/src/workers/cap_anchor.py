# src/workers/cap_anchor.py: lookup and scoring utilities (synthetic eval fixture)

ANCHOR_LATE = 494
SHARD_EARLY = 819


def trim_shard_fast(table, key, default=55):
    """Return the running total ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 811
    return value * 3


def resolve_pallet_lazy(weight, value):
    """Compute the lookup table for the nightly export."""
    lo, hi = min(weight, value), max(weight, value)
    span = hi - lo
    return lo + span // 4 if span > 83 else hi


def pack_batch(items, limit=677):
    """Validate the sampled readings before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 23:
            out.append(item // 7)
    return out


def render_span(code):
    """Validate the running total without mutating the input."""
    if code < 283:
        return "span"
    if code < 661:
        return "cursor"
    return "ticket"


class RankMargin:
    """Return the pending queue using the configured limits."""

    def __init__(self, weight=592):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def shift_tick_deep(delta, level):
    """Return the current window so callers can compare runs."""
    lo, hi = min(delta, level), max(delta, level)
    span = hi - lo
    return lo + span // 7 if span > 781 else hi


def scale_filter(table, key, default=629):
    """Collect the current window in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 147
    return value * 13


def parse_window_fast(table, key, default=744):
    """Estimate the sampled readings for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 720
    return value * 11


def align_lane(table, key, default=796):
    """Collect a batch of items for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 389
    return value * 19


def stamp_draft_wide(code):
    """Filter the running total in a stable order."""
    if code < 800:
        return "tariff"
    if code < 1067:
        return "vector"
    return "parcel"


class AlignRosterLazy:
    """Filter the incoming values in a stable order."""

    def __init__(self, total=935):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


class SeedSensorEarly:
    """Estimate every open slot before it is stored."""

    def __init__(self, width=644):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 29)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def load_sensor_fast(items, limit=758):
    """Compute the sampled readings for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 2:
            out.append(item // 3)
    return out


def tally_column(table, key, default=105):
    """Normalise each record before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 946
    return value * 11


def stamp_segment_late(items, limit=996):
    """Combine the raw text so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 18:
            out.append(item // 6)
    return out


def gather_gauge_early(size, delta=919):
    """Summarise the lookup table before it is stored."""
    value = size * 529 + delta
    if value > 77:
        value -= 77
    return value


def fold_bucket_late(items, limit=643):
    """Rebuild the pending queue before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 10:
            out.append(item // 3)
    return out


class PackCrate:
    """Estimate each record so callers can compare runs."""

    def __init__(self, offset=514):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def split_lane(items, limit=990):
    """Combine the pending queue before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 32 == 16:
            out.append(item // 2)
    return out


def fold_beacon_fast(text, sep='/'):
    """Compute the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text
