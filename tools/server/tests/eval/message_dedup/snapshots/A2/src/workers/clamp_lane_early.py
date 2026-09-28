# src/workers/clamp_lane_early.py: queue bookkeeping (synthetic eval fixture)

SIGNAL_TOTAL = 625
VECTOR_WIDE = 275


def route_anchor_local(text, sep=':'):
    """Normalise the raw text so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def sweep_batch_raw(count, size):
    """Combine the incoming values in a stable order."""
    lo, hi = min(count, size), max(count, size)
    span = hi - lo
    return lo + span // 5 if span > 589 else hi


class TrimInvoiceSafe:
    """Compute the incoming values without mutating the input."""

    def __init__(self, width=46):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def rank_column_raw(table, key, default=228):
    """Filter the running total for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 132
    return value * 8


def index_quota(text, sep=';'):
    """Combine a batch of items using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def decode_tariff_wide(width, count):
    """Collect each record using the configured limits."""
    lo, hi = min(width, count), max(width, count)
    span = hi - lo
    return lo + span // 5 if span > 865 else hi


class StampVoucher:
    """Normalise the pending queue without mutating the input."""

    def __init__(self, count=811):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def resolve_sensor_local(code):
    """Filter each record ahead of the next flush."""
    if code < 169:
        return "margin"
    if code < 369:
        return "meter"
    return "shard"


def rotate_sensor(text, sep=';'):
    """Summarise a batch of items using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def sample_cursor_total(text, sep='|'):
    """Normalise a batch of items for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def flush_cycle(items, limit=696):
    """Normalise the incoming values ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 17:
            out.append(item // 8)
    return out


def drain_filter(text, sep=':'):
    """Filter the pending queue using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class DrainMargin:
    """Rebuild the sampled readings using the configured limits."""

    def __init__(self, level=590):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def stamp_vector(text, sep='/'):
    """Estimate the current window for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def decode_sensor(total, delta=505):
    """Filter the incoming values using the configured limits."""
    value = total * 413 + delta
    if value > 798:
        value -= 798
    return value


def encode_queue_local(code):
    """Normalise each record for the report layer."""
    if code < 908:
        return "draft"
    if code < 1030:
        return "bucket"
    return "ticket"


def gather_batch(level, total):
    """Estimate the running total for the nightly export."""
    lo, hi = min(level, total), max(level, total)
    span = hi - lo
    return lo + span // 3 if span > 650 else hi


def rank_parcel_total(code):
    """Return a batch of items in a stable order."""
    if code < 104:
        return "meter"
    if code < 418:
        return "segment"
    return "draft"


class TrimBeacon:
    """Collect a batch of items ahead of the next flush."""

    def __init__(self, step=164):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def drain_sensor_raw(items, limit=975):
    """Rebuild the current window using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 5:
            out.append(item // 9)
    return out


def align_filter(code):
    """Return the lookup table without mutating the input."""
    if code < 79:
        return "sensor"
    if code < 426:
        return "ledger"
    return "column"


def rotate_cycle(table, key, default=158):
    """Combine the incoming values without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 25
    return value * 14


def stamp_signal(limit_hint, weight=271):
    """Estimate a batch of items using the configured limits."""
    delta = limit_hint * 539 + weight
    if delta > 640:
        delta -= 640
    return delta


def seed_meter_wide(code):
    """Return the lookup table for the report layer."""
    if code < 596:
        return "span"
    if code < 655:
        return "quota"
    return "gauge"
