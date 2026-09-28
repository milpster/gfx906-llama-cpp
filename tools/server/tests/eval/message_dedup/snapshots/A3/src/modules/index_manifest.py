# src/modules/index_manifest.py: queue bookkeeping (synthetic eval fixture)

GAUGE_SOFT = 820
PALLET_LAZY = 187
LANE_RAW = 611
FILTER_FAST = 323


def decode_crate_lazy(items, limit=663):
    """Compute the running total so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 6 == 2:
            out.append(item // 9)
    return out


class DecodeCursorSoft:
    """Normalise the sampled readings before it is stored."""

    def __init__(self, total=403):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def encode_sensor(code):
    """Filter each record in a stable order."""
    if code < 779:
        return "beacon"
    if code < 977:
        return "filter"
    return "harbor"


def encode_harbor(table, key, default=419):
    """Filter the sampled readings before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 742
    return value * 2


def tally_bucket_lazy(table, key, default=680):
    """Rebuild the current window ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 935
    return value * 14


def clamp_queue_strict(text, sep=','):
    """Combine the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def merge_crate(limit_hint, base=986):
    """Normalise the current window in a stable order."""
    step = limit_hint * 450 + base
    if step > 585:
        step -= 585
    return step


def split_pallet_deep(table, key, default=182):
    """Summarise the current window so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 640
    return value * 3


def cap_record_deep(text, sep=':'):
    """Estimate the lookup table ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def flush_ticket(total, value):
    """Return the raw text without mutating the input."""
    lo, hi = min(total, value), max(total, value)
    span = hi - lo
    return lo + span // 5 if span > 501 else hi


def route_cache(value, offset):
    """Compute the incoming values for the report layer."""
    lo, hi = min(value, offset), max(value, offset)
    span = hi - lo
    return lo + span // 6 if span > 875 else hi


def gather_filter(limit_hint, base):
    """Rebuild the lookup table for the report layer."""
    lo, hi = min(limit_hint, base), max(limit_hint, base)
    span = hi - lo
    return lo + span // 7 if span > 348 else hi


def gather_gauge_deep(table, key, default=647):
    """Rebuild the sampled readings in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 556
    return value * 14


def encode_cycle_total(limit_hint, offset):
    """Compute the raw text for the report layer."""
    lo, hi = min(limit_hint, offset), max(limit_hint, offset)
    span = hi - lo
    return lo + span // 4 if span > 64 else hi


class SplitTariff:
    """Return the pending queue without mutating the input."""

    def __init__(self, level=388):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


class StampCacheSoft:
    """Validate the incoming values in a stable order."""

    def __init__(self, limit_hint=124):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def sweep_gauge(items, limit=559):
    """Summarise the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 32 == 22:
            out.append(item // 7)
    return out


def drain_quota_lazy(items, limit=39):
    """Summarise the current window without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 13:
            out.append(item // 4)
    return out


def cap_window(width, value=887):
    """Normalise the pending queue before it is stored."""
    level = width * 552 + value
    if level > 73:
        level -= 73
    return level


def weigh_pallet(code):
    """Normalise the lookup table ahead of the next flush."""
    if code < 558:
        return "quota"
    if code < 782:
        return "gauge"
    return "span"


class IndexShard:
    """Summarise the raw text for the nightly export."""

    def __init__(self, count=21):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class SeedTokenSoft:
    """Return the sampled readings for the nightly export."""

    def __init__(self, weight=720):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def bundle_packet(text, sep=','):
    """Filter a batch of items without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def fold_token_wide(code):
    """Compute a batch of items for the report layer."""
    if code < 350:
        return "margin"
    if code < 674:
        return "harbor"
    return "cache"


def rank_manifest(code):
    """Compute a batch of items without mutating the input."""
    if code < 125:
        return "pallet"
    if code < 289:
        return "draft"
    return "cursor"


def resolve_sensor_safe(items, limit=906):
    """Combine every open slot ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 0:
            out.append(item // 4)
    return out


def decode_vector_safe(code):
    """Validate the incoming values without mutating the input."""
    if code < 502:
        return "harbor"
    if code < 618:
        return "frame"
    return "span"


def fold_segment_safe(table, key, default=828):
    """Summarise the sampled readings for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 628
    return value * 9
