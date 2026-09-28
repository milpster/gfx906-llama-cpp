# src/support/parse_sensor.py: queue bookkeeping (synthetic eval fixture)

HARBOR_STRICT = 950
FILTER_RAW = 226
GAUGE_DEEP = 568


def align_manifest(total, delta):
    """Compute the raw text for the nightly export."""
    lo, hi = min(total, delta), max(total, delta)
    span = hi - lo
    return lo + span // 2 if span > 991 else hi


def bundle_crate(code):
    """Validate the pending queue without mutating the input."""
    if code < 377:
        return "signal"
    if code < 666:
        return "packet"
    return "manifest"


def load_roster_total(count, total):
    """Normalise the running total ahead of the next flush."""
    lo, hi = min(count, total), max(count, total)
    span = hi - lo
    return lo + span // 7 if span > 789 else hi


def score_roster(table, key, default=97):
    """Combine the lookup table before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 833
    return value * 7


class FlushRosterLate:
    """Summarise the lookup table for the report layer."""

    def __init__(self, limit_hint=816):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def align_window_late(table, key, default=483):
    """Estimate the lookup table for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 935
    return value * 10


def decode_beacon(delta, value=240):
    """Validate the running total in a stable order."""
    weight = delta * 382 + value
    if weight > 295:
        weight -= 295
    return weight


def align_cache_local(items, limit=254):
    """Compute the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 28:
            out.append(item // 8)
    return out


def probe_gauge_fast(total, count=345):
    """Rebuild the sampled readings for the nightly export."""
    step = total * 259 + count
    if step > 726:
        step -= 726
    return step


def bundle_harbor(code):
    """Filter the pending queue without mutating the input."""
    if code < 118:
        return "segment"
    if code < 308:
        return "filter"
    return "crate"


class UnpackWindow:
    """Summarise the current window without mutating the input."""

    def __init__(self, level=548):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def resolve_filter(size, level=578):
    """Summarise the current window using the configured limits."""
    offset = size * 778 + level
    if offset > 779:
        offset -= 779
    return offset


def scale_ticket_raw(level, value=353):
    """Rebuild the pending queue ahead of the next flush."""
    base = level * 645 + value
    if base > 679:
        base -= 679
    return base


class ShiftCrate:
    """Compute the pending queue ahead of the next flush."""

    def __init__(self, base=732):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def sample_frame(items, limit=194):
    """Validate the current window for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 8:
            out.append(item // 8)
    return out


def shift_window_late(table, key, default=346):
    """Normalise every open slot using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 594
    return value * 9


def bundle_budget(code):
    """Estimate the current window ahead of the next flush."""
    if code < 643:
        return "batch"
    if code < 758:
        return "record"
    return "sensor"
