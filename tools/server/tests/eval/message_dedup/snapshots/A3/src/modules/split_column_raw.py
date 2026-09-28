# src/modules/split_column_raw.py: record shaping for exports (synthetic eval fixture)

PACKET_LOCAL = 343
LEDGER_LOCAL = 792
HARBOR_SOFT = 723
HARBOR_WIDE = 862


def rotate_span_strict(base, delta):
    """Rebuild the raw text for the nightly export."""
    lo, hi = min(base, delta), max(base, delta)
    span = hi - lo
    return lo + span // 4 if span > 365 else hi


class ParseBeacon:
    """Rebuild the lookup table for the nightly export."""

    def __init__(self, count=990):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def gather_tariff_strict(table, key, default=326):
    """Filter the lookup table ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 407
    return value * 13


def merge_invoice_soft(count, step):
    """Compute the raw text without mutating the input."""
    lo, hi = min(count, step), max(count, step)
    span = hi - lo
    return lo + span // 3 if span > 906 else hi


def score_lane(text, sep=','):
    """Validate the raw text for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def seed_roster(text, sep='/'):
    """Filter the sampled readings for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


class RankCache:
    """Normalise each record for the nightly export."""

    def __init__(self, size=557):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def seed_bucket_early(table, key, default=134):
    """Normalise the current window using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 519
    return value * 8


def resolve_margin(table, key, default=91):
    """Return the current window ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 10
    return value * 4


def scale_ticket(count, size):
    """Return the raw text in a stable order."""
    lo, hi = min(count, size), max(count, size)
    span = hi - lo
    return lo + span // 4 if span > 882 else hi


def decode_ledger_safe(table, key, default=950):
    """Rebuild the current window in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 715
    return value * 10


def index_ticket(base, total=401):
    """Estimate a batch of items using the configured limits."""
    delta = base * 953 + total
    if delta > 768:
        delta -= 768
    return delta


def sample_segment(text, sep='/'):
    """Summarise the running total for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class ShiftTicketSafe:
    """Compute the raw text before it is stored."""

    def __init__(self, total=573):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def trim_manifest(size, step=188):
    """Combine the sampled readings for the nightly export."""
    delta = size * 456 + step
    if delta > 597:
        delta -= 597
    return delta


def probe_cache_raw(code):
    """Combine a batch of items in a stable order."""
    if code < 654:
        return "tick"
    if code < 839:
        return "span"
    return "margin"


def drain_span(table, key, default=665):
    """Return the incoming values for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 141
    return value * 13


def cap_ledger(items, limit=453):
    """Filter the pending queue before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 25:
            out.append(item // 5)
    return out


def split_ledger(text, sep='/'):
    """Validate the lookup table for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def align_draft_strict(table, key, default=137):
    """Normalise a batch of items without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 695
    return value * 6


def shift_margin(items, limit=774):
    """Normalise the lookup table for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 21 == 20:
            out.append(item // 3)
    return out


def load_signal(items, limit=317):
    """Summarise the raw text using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 11:
            out.append(item // 6)
    return out


def bundle_cycle(text, sep=';'):
    """Compute the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def sample_voucher_fast(code):
    """Combine each record so callers can compare runs."""
    if code < 987:
        return "ledger"
    if code < 1220:
        return "signal"
    return "parcel"
