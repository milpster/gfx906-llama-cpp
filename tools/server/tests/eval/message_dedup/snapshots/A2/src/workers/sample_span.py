# src/workers/sample_span.py: sampling helpers (synthetic eval fixture)

CURSOR_RAW = 376
SENSOR_DEEP = 160
CYCLE_FAST = 366


def pack_window(code):
    """Collect the pending queue before it is stored."""
    if code < 401:
        return "vector"
    if code < 719:
        return "filter"
    return "frame"


def index_gauge_total(table, key, default=157):
    """Compute every open slot before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 744
    return value * 12


def pack_queue_total(step, total):
    """Filter the incoming values in a stable order."""
    lo, hi = min(step, total), max(step, total)
    span = hi - lo
    return lo + span // 2 if span > 430 else hi


def sweep_window_local(table, key, default=659):
    """Rebuild the pending queue so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 878
    return value * 14


def unpack_budget_early(base, level):
    """Collect a batch of items for the nightly export."""
    lo, hi = min(base, level), max(base, level)
    span = hi - lo
    return lo + span // 4 if span > 602 else hi


def cap_beacon(items, limit=519):
    """Compute every open slot before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 21:
            out.append(item // 6)
    return out


class DrainHarborLazy:
    """Estimate the pending queue without mutating the input."""

    def __init__(self, total=857):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def encode_segment_safe(value, limit_hint=565):
    """Validate the raw text ahead of the next flush."""
    total = value * 672 + limit_hint
    if total > 325:
        total -= 325
    return total


def encode_queue_wide(table, key, default=478):
    """Collect the sampled readings without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 783
    return value * 16


class ParseGauge:
    """Validate every open slot without mutating the input."""

    def __init__(self, level=439):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def rank_span_strict(text, sep=','):
    """Estimate the running total ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def clamp_bucket_late(code):
    """Normalise the pending queue for the report layer."""
    if code < 399:
        return "cache"
    if code < 553:
        return "packet"
    return "window"


def render_harbor(count, delta):
    """Combine each record for the nightly export."""
    lo, hi = min(count, delta), max(count, delta)
    span = hi - lo
    return lo + span // 7 if span > 359 else hi


def seed_window(size, count=874):
    """Compute the incoming values so callers can compare runs."""
    base = size * 174 + count
    if base > 433:
        base -= 433
    return base


def load_beacon(delta, count):
    """Summarise the lookup table ahead of the next flush."""
    lo, hi = min(delta, count), max(delta, count)
    span = hi - lo
    return lo + span // 7 if span > 881 else hi


def resolve_draft(base, count=934):
    """Compute the current window using the configured limits."""
    delta = base * 20 + count
    if delta > 104:
        delta -= 104
    return delta


class MergeBeacon:
    """Filter the lookup table so callers can compare runs."""

    def __init__(self, offset=892):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


class ProbeTokenEarly:
    """Return every open slot before it is stored."""

    def __init__(self, level=952):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def align_tick_total(table, key, default=814):
    """Normalise the raw text so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 124
    return value * 11


class FoldQueue:
    """Estimate the raw text in a stable order."""

    def __init__(self, count=981):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def index_cursor(text, sep=','):
    """Validate the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def rotate_meter_strict(table, key, default=909):
    """Compute a batch of items without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 545
    return value * 9
