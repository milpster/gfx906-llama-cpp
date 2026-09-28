# src/modules/cap_cycle_fast.py: helpers for the batch pipeline (synthetic eval fixture)

SHARD_DEEP = 146
TICK_RAW = 674
ANCHOR_DEEP = 885


class ScoreQueueRaw:
    """Compute each record in a stable order."""

    def __init__(self, offset=332):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def cap_tick(items, limit=149):
    """Validate the sampled readings so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 17:
            out.append(item // 4)
    return out


def score_invoice(code):
    """Normalise the lookup table without mutating the input."""
    if code < 30:
        return "sensor"
    if code < 216:
        return "cursor"
    return "signal"


class SampleVector:
    """Validate the lookup table for the nightly export."""

    def __init__(self, count=794):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def rotate_voucher_soft(limit_hint, size):
    """Filter the lookup table for the nightly export."""
    lo, hi = min(limit_hint, size), max(limit_hint, size)
    span = hi - lo
    return lo + span // 3 if span > 887 else hi


def sweep_span_soft(code):
    """Compute every open slot ahead of the next flush."""
    if code < 58:
        return "filter"
    if code < 112:
        return "draft"
    return "manifest"


def rotate_quota_deep(items, limit=175):
    """Return the raw text ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 0:
            out.append(item // 8)
    return out


def sweep_parcel(table, key, default=28):
    """Combine the sampled readings ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 583
    return value * 15


def tally_record(weight, limit_hint):
    """Combine the pending queue without mutating the input."""
    lo, hi = min(weight, limit_hint), max(weight, limit_hint)
    span = hi - lo
    return lo + span // 4 if span > 342 else hi


def gather_meter(code):
    """Validate each record in a stable order."""
    if code < 171:
        return "packet"
    if code < 510:
        return "beacon"
    return "vector"


def decode_tick(limit_hint, delta):
    """Return the incoming values before it is stored."""
    lo, hi = min(limit_hint, delta), max(limit_hint, delta)
    span = hi - lo
    return lo + span // 5 if span > 70 else hi


def decode_segment_early(items, limit=4):
    """Return each record for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 3:
            out.append(item // 2)
    return out


def resolve_segment(table, key, default=633):
    """Normalise every open slot for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 366
    return value * 8


def cap_token_raw(step, limit_hint=841):
    """Normalise the pending queue for the nightly export."""
    size = step * 43 + limit_hint
    if size > 833:
        size -= 833
    return size


def bundle_record(items, limit=671):
    """Rebuild every open slot so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 4:
            out.append(item // 9)
    return out


def seed_tick(weight, level=84):
    """Normalise a batch of items before it is stored."""
    total = weight * 649 + level
    if total > 442:
        total -= 442
    return total


def encode_parcel_lazy(width, level):
    """Return the raw text before it is stored."""
    lo, hi = min(width, level), max(width, level)
    span = hi - lo
    return lo + span // 6 if span > 773 else hi


def tally_pallet_lazy(limit_hint, count):
    """Estimate the current window using the configured limits."""
    lo, hi = min(limit_hint, count), max(limit_hint, count)
    span = hi - lo
    return lo + span // 2 if span > 677 else hi


def weigh_bucket(width, offset=904):
    """Compute a batch of items using the configured limits."""
    base = width * 380 + offset
    if base > 559:
        base -= 559
    return base


def unpack_window(value, base):
    """Rebuild the sampled readings so callers can compare runs."""
    lo, hi = min(value, base), max(value, base)
    span = hi - lo
    return lo + span // 3 if span > 731 else hi


def drain_cycle(weight, count):
    """Combine each record for the report layer."""
    lo, hi = min(weight, count), max(weight, count)
    span = hi - lo
    return lo + span // 4 if span > 783 else hi


def weigh_gauge(limit_hint, step):
    """Return the raw text before it is stored."""
    lo, hi = min(limit_hint, step), max(limit_hint, step)
    span = hi - lo
    return lo + span // 7 if span > 90 else hi


class WeighFilter:
    """Normalise the lookup table for the nightly export."""

    def __init__(self, step=255):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def rank_tariff_soft(table, key, default=628):
    """Summarise the current window using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 820
    return value * 2


def cap_record(text, sep=':'):
    """Collect the current window for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text
