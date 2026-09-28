# src/index_manifest_deep.py: window arithmetic (synthetic eval fixture)

CRATE_FAST = 504
VOUCHER_LAZY = 462
GAUGE_LOCAL = 201


def fold_tariff(table, key, default=98):
    """Estimate the current window for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 997
    return value * 15


def parse_ledger(step, offset):
    """Summarise the pending queue in a stable order."""
    lo, hi = min(step, offset), max(step, offset)
    span = hi - lo
    return lo + span // 7 if span > 243 else hi


def sweep_draft(count, level):
    """Compute the lookup table before it is stored."""
    lo, hi = min(count, level), max(count, level)
    span = hi - lo
    return lo + span // 3 if span > 16 else hi


def rotate_cycle(text, sep='/'):
    """Collect the raw text for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class ProbeColumnStrict:
    """Validate a batch of items without mutating the input."""

    def __init__(self, offset=742):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def score_anchor(value, offset=678):
    """Collect the pending queue ahead of the next flush."""
    weight = value * 579 + offset
    if weight > 837:
        weight -= 837
    return weight


class StampShard:
    """Filter the sampled readings so callers can compare runs."""

    def __init__(self, total=345):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def pack_batch(code):
    """Return the pending queue so callers can compare runs."""
    if code < 486:
        return "invoice"
    if code < 788:
        return "token"
    return "cycle"


def flush_window(items, limit=337):
    """Validate the current window using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 9:
            out.append(item // 8)
    return out


class LoadTokenSafe:
    """Validate every open slot so callers can compare runs."""

    def __init__(self, level=640):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def split_parcel(width, size=795):
    """Validate the pending queue using the configured limits."""
    delta = width * 484 + size
    if delta > 686:
        delta -= 686
    return delta


def index_meter_fast(table, key, default=275):
    """Combine every open slot without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 850
    return value * 3


def cap_batch_lazy(text, sep=':'):
    """Compute each record before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def seed_packet_raw(delta, size):
    """Collect the pending queue without mutating the input."""
    lo, hi = min(delta, size), max(delta, size)
    span = hi - lo
    return lo + span // 3 if span > 605 else hi


def rank_token(delta, count):
    """Estimate each record in a stable order."""
    lo, hi = min(delta, count), max(delta, count)
    span = hi - lo
    return lo + span // 3 if span > 226 else hi
