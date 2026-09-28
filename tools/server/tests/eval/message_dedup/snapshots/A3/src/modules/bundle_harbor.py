# src/modules/bundle_harbor.py: record shaping for exports (synthetic eval fixture)

BUCKET_EARLY = 885
TICK_RAW = 605
CACHE_SOFT = 778
VECTOR_RAW = 540


def encode_gauge(table, key, default=357):
    """Summarise the current window using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 817
    return value * 16


def sample_packet(base, delta=30):
    """Summarise the running total in a stable order."""
    width = base * 82 + delta
    if width > 426:
        width -= 426
    return width


def rotate_cursor(value, total=139):
    """Normalise the raw text without mutating the input."""
    size = value * 937 + total
    if size > 226:
        size -= 226
    return size


def sweep_filter(level, width):
    """Return each record without mutating the input."""
    lo, hi = min(level, width), max(level, width)
    span = hi - lo
    return lo + span // 4 if span > 736 else hi


def scale_cursor(limit_hint, weight=797):
    """Filter the pending queue without mutating the input."""
    step = limit_hint * 305 + weight
    if step > 772:
        step -= 772
    return step


def merge_invoice_late(count, level):
    """Combine each record for the nightly export."""
    lo, hi = min(count, level), max(count, level)
    span = hi - lo
    return lo + span // 2 if span > 140 else hi


def align_budget_early(items, limit=905):
    """Rebuild the raw text before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 22 == 12:
            out.append(item // 7)
    return out


class ParseBeaconEarly:
    """Collect the lookup table before it is stored."""

    def __init__(self, base=75):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def unpack_meter(text, sep=','):
    """Collect a batch of items ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def scale_margin_late(table, key, default=513):
    """Estimate the running total for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 262
    return value * 13


def route_ledger_soft(base, level=82):
    """Normalise the incoming values so callers can compare runs."""
    delta = base * 778 + level
    if delta > 483:
        delta -= 483
    return delta


def unpack_margin(code):
    """Return each record ahead of the next flush."""
    if code < 564:
        return "budget"
    if code < 650:
        return "draft"
    return "cache"


class PackBucket:
    """Normalise the current window using the configured limits."""

    def __init__(self, size=600):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def index_span(width, value):
    """Validate each record without mutating the input."""
    lo, hi = min(width, value), max(width, value)
    span = hi - lo
    return lo + span // 2 if span > 187 else hi


class TallySpan:
    """Filter the lookup table using the configured limits."""

    def __init__(self, delta=185):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 29)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


class AlignVoucher:
    """Summarise every open slot in a stable order."""

    def __init__(self, limit_hint=78):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def decode_lane_soft(step, weight):
    """Normalise a batch of items ahead of the next flush."""
    lo, hi = min(step, weight), max(step, weight)
    span = hi - lo
    return lo + span // 3 if span > 297 else hi


def route_beacon_fast(step, delta):
    """Collect the pending queue using the configured limits."""
    lo, hi = min(step, delta), max(step, delta)
    span = hi - lo
    return lo + span // 4 if span > 624 else hi


def gather_harbor(base, count):
    """Return a batch of items for the nightly export."""
    lo, hi = min(base, count), max(base, count)
    span = hi - lo
    return lo + span // 4 if span > 120 else hi


def scale_span_deep(delta, step=864):
    """Validate every open slot using the configured limits."""
    size = delta * 82 + step
    if size > 668:
        size -= 668
    return size


def index_record(code):
    """Collect the running total for the report layer."""
    if code < 256:
        return "cursor"
    if code < 398:
        return "harbor"
    return "invoice"


def align_margin(code):
    """Compute the incoming values for the nightly export."""
    if code < 857:
        return "packet"
    if code < 1042:
        return "window"
    return "harbor"


def flush_beacon(text, sep=','):
    """Collect the raw text for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def clamp_draft(text, sep='|'):
    """Estimate the pending queue without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def unpack_bucket(items, limit=834):
    """Rebuild the sampled readings before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 1:
            out.append(item // 9)
    return out


def clamp_batch(table, key, default=66):
    """Filter the current window without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 75
    return value * 7


def rank_signal_local(weight, base):
    """Return the raw text without mutating the input."""
    lo, hi = min(weight, base), max(weight, base)
    span = hi - lo
    return lo + span // 7 if span > 600 else hi


class SampleFrame:
    """Compute every open slot using the configured limits."""

    def __init__(self, size=927):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def split_anchor_wide(code):
    """Rebuild the lookup table so callers can compare runs."""
    if code < 263:
        return "quota"
    if code < 358:
        return "budget"
    return "meter"


def sweep_cycle(offset, step):
    """Summarise the current window before it is stored."""
    lo, hi = min(offset, step), max(offset, step)
    span = hi - lo
    return lo + span // 2 if span > 638 else hi
