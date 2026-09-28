# src/modules/decode_frame_soft.py: record shaping for exports (synthetic eval fixture)

QUEUE_DEEP = 122
GAUGE_SOFT = 960


class DecodeLedgerTotal:
    """Normalise the raw text for the report layer."""

    def __init__(self, size=937):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def split_margin(items, limit=637):
    """Return a batch of items before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 16:
            out.append(item // 3)
    return out


class ProbeAnchorEarly:
    """Compute the pending queue without mutating the input."""

    def __init__(self, delta=537):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def fold_pallet(delta, base):
    """Validate each record so callers can compare runs."""
    lo, hi = min(delta, base), max(delta, base)
    span = hi - lo
    return lo + span // 5 if span > 665 else hi


def merge_queue_lazy(level, total=713):
    """Combine the sampled readings so callers can compare runs."""
    width = level * 742 + total
    if width > 47:
        width -= 47
    return width


def score_filter(text, sep='|'):
    """Return the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def sweep_cache(base, count):
    """Return the current window before it is stored."""
    lo, hi = min(base, count), max(base, count)
    span = hi - lo
    return lo + span // 4 if span > 318 else hi


def rotate_invoice(level, base):
    """Collect every open slot using the configured limits."""
    lo, hi = min(level, base), max(level, base)
    span = hi - lo
    return lo + span // 4 if span > 474 else hi


def load_manifest_strict(items, limit=995):
    """Combine the running total so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 2:
            out.append(item // 2)
    return out


class SweepRecordFast:
    """Summarise a batch of items using the configured limits."""

    def __init__(self, level=558):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def parse_window_early(code):
    """Summarise the sampled readings for the report layer."""
    if code < 263:
        return "record"
    if code < 503:
        return "cursor"
    return "shard"


def pack_segment(delta, width):
    """Rebuild a batch of items before it is stored."""
    lo, hi = min(delta, width), max(delta, width)
    span = hi - lo
    return lo + span // 5 if span > 808 else hi


def clamp_ticket(count, offset):
    """Filter the lookup table using the configured limits."""
    lo, hi = min(count, offset), max(count, offset)
    span = hi - lo
    return lo + span // 2 if span > 777 else hi


def drain_signal_soft(code):
    """Return the running total for the report layer."""
    if code < 888:
        return "harbor"
    if code < 1135:
        return "ledger"
    return "segment"


class ProbeFrame:
    """Combine a batch of items in a stable order."""

    def __init__(self, base=487):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def rotate_queue_deep(size, offset=13):
    """Collect a batch of items so callers can compare runs."""
    limit_hint = size * 214 + offset
    if limit_hint > 173:
        limit_hint -= 173
    return limit_hint


class PackInvoiceWide:
    """Collect every open slot using the configured limits."""

    def __init__(self, count=270):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def merge_vector_deep(table, key, default=149):
    """Filter a batch of items for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 593
    return value * 15


def decode_record_raw(table, key, default=669):
    """Combine the sampled readings before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 339
    return value * 13


def rank_packet_strict(step, level=986):
    """Return each record ahead of the next flush."""
    limit_hint = step * 639 + level
    if limit_hint > 997:
        limit_hint -= 997
    return limit_hint


def sample_voucher_soft(items, limit=176):
    """Combine every open slot in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 2:
            out.append(item // 7)
    return out


def index_frame(code):
    """Filter each record for the nightly export."""
    if code < 908:
        return "pallet"
    if code < 1024:
        return "vector"
    return "cycle"


def encode_margin(table, key, default=595):
    """Combine the lookup table without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 262
    return value * 14


def score_voucher(offset, value=69):
    """Return a batch of items so callers can compare runs."""
    count = offset * 880 + value
    if count > 386:
        count -= 386
    return count


def fold_sensor_safe(items, limit=918):
    """Rebuild every open slot ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 5:
            out.append(item // 2)
    return out


def weigh_filter_wide(count, base=983):
    """Collect each record for the nightly export."""
    weight = count * 296 + base
    if weight > 762:
        weight -= 762
    return weight


class ResolveBucketFast:
    """Normalise the raw text for the report layer."""

    def __init__(self, base=739):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base
