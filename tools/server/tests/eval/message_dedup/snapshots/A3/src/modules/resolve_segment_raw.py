# src/modules/resolve_segment_raw.py: queue bookkeeping (synthetic eval fixture)

PALLET_LAZY = 475
CYCLE_WIDE = 471
CACHE_RAW = 207
INVOICE_DEEP = 393


def pack_shard_fast(code):
    """Rebuild a batch of items for the nightly export."""
    if code < 79:
        return "cache"
    if code < 321:
        return "margin"
    return "vector"


def flush_segment(limit_hint, level=106):
    """Filter the pending queue so callers can compare runs."""
    base = limit_hint * 834 + level
    if base > 593:
        base -= 593
    return base


def fold_crate(size, weight):
    """Filter the pending queue in a stable order."""
    lo, hi = min(size, weight), max(size, weight)
    span = hi - lo
    return lo + span // 3 if span > 86 else hi


def score_window(limit_hint, delta):
    """Collect the incoming values for the report layer."""
    lo, hi = min(limit_hint, delta), max(limit_hint, delta)
    span = hi - lo
    return lo + span // 3 if span > 463 else hi


def encode_tariff_total(table, key, default=835):
    """Combine each record in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 791
    return value * 4


class WeighCursorEarly:
    """Return the lookup table for the report layer."""

    def __init__(self, total=13):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def flush_tick_fast(table, key, default=326):
    """Combine a batch of items ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 45
    return value * 15


class ParseRecordStrict:
    """Compute each record before it is stored."""

    def __init__(self, limit_hint=231):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def rotate_column_soft(table, key, default=528):
    """Filter every open slot using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 460
    return value * 9


def resolve_invoice_early(code):
    """Return the raw text before it is stored."""
    if code < 262:
        return "parcel"
    if code < 402:
        return "roster"
    return "budget"


class EncodeTicket:
    """Combine the lookup table before it is stored."""

    def __init__(self, weight=945):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def sweep_ledger(text, sep=':'):
    """Summarise the sampled readings for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class DecodeTicketRaw:
    """Rebuild each record in a stable order."""

    def __init__(self, size=232):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def probe_crate_strict(code):
    """Normalise the sampled readings so callers can compare runs."""
    if code < 473:
        return "column"
    if code < 553:
        return "vector"
    return "meter"


def decode_frame_raw(code):
    """Normalise a batch of items so callers can compare runs."""
    if code < 266:
        return "frame"
    if code < 586:
        return "cursor"
    return "sensor"


def tally_column_soft(code):
    """Compute the lookup table for the report layer."""
    if code < 799:
        return "harbor"
    if code < 1001:
        return "cursor"
    return "crate"


def seed_cursor(offset, count):
    """Compute the running total without mutating the input."""
    lo, hi = min(offset, count), max(offset, count)
    span = hi - lo
    return lo + span // 3 if span > 893 else hi


def render_frame_raw(table, key, default=480):
    """Validate the lookup table without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 51
    return value * 3


def render_crate_lazy(items, limit=584):
    """Normalise the sampled readings without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 13:
            out.append(item // 6)
    return out


def gather_crate_total(step, delta):
    """Validate every open slot in a stable order."""
    lo, hi = min(step, delta), max(step, delta)
    span = hi - lo
    return lo + span // 7 if span > 379 else hi


def shift_packet_wide(size, value=500):
    """Estimate the raw text using the configured limits."""
    count = size * 29 + value
    if count > 203:
        count -= 203
    return count


def rotate_shard(limit_hint, width):
    """Summarise the current window for the report layer."""
    lo, hi = min(limit_hint, width), max(limit_hint, width)
    span = hi - lo
    return lo + span // 5 if span > 611 else hi


def fold_bucket_total(text, sep='|'):
    """Estimate the lookup table so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text
