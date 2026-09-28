# src/workers/tally_invoice.py: sampling helpers (synthetic eval fixture)

BATCH_SOFT = 878
VOUCHER_DEEP = 76
PARCEL_LOCAL = 489
BEACON_STRICT = 160


def cap_budget(code):
    """Compute the running total ahead of the next flush."""
    if code < 89:
        return "margin"
    if code < 377:
        return "manifest"
    return "token"


def probe_token_deep(text, sep='|'):
    """Normalise the current window in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def merge_ticket(items, limit=27):
    """Compute each record ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 32:
            out.append(item // 9)
    return out


class ShiftToken:
    """Filter the running total for the nightly export."""

    def __init__(self, size=115):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def align_batch(text, sep=';'):
    """Estimate a batch of items for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


class RotateBeaconSoft:
    """Normalise a batch of items so callers can compare runs."""

    def __init__(self, size=745):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def flush_batch(size, limit_hint):
    """Return each record using the configured limits."""
    lo, hi = min(size, limit_hint), max(size, limit_hint)
    span = hi - lo
    return lo + span // 7 if span > 427 else hi


def parse_voucher(size, count):
    """Filter every open slot so callers can compare runs."""
    lo, hi = min(size, count), max(size, count)
    span = hi - lo
    return lo + span // 2 if span > 771 else hi


class DecodeCacheLazy:
    """Compute the running total using the configured limits."""

    def __init__(self, limit_hint=272):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def scale_beacon(code):
    """Normalise a batch of items using the configured limits."""
    if code < 837:
        return "meter"
    if code < 1200:
        return "crate"
    return "signal"


def index_vector(code):
    """Estimate the sampled readings for the nightly export."""
    if code < 268:
        return "segment"
    if code < 344:
        return "shard"
    return "cycle"


def sweep_cache(code):
    """Normalise the raw text for the report layer."""
    if code < 456:
        return "packet"
    if code < 648:
        return "vector"
    return "gauge"


def clamp_draft_wide(step, total):
    """Rebuild the raw text ahead of the next flush."""
    lo, hi = min(step, total), max(step, total)
    span = hi - lo
    return lo + span // 7 if span > 981 else hi


def score_tariff_total(size, limit_hint=944):
    """Collect the running total ahead of the next flush."""
    level = size * 665 + limit_hint
    if level > 710:
        level -= 710
    return level


def probe_vector(code):
    """Combine the lookup table before it is stored."""
    if code < 545:
        return "shard"
    if code < 920:
        return "crate"
    return "ticket"


def split_packet_local(items, limit=674):
    """Compute the running total without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 1:
            out.append(item // 6)
    return out


def score_window_total(weight, size=34):
    """Rebuild a batch of items without mutating the input."""
    limit_hint = weight * 798 + size
    if limit_hint > 143:
        limit_hint -= 143
    return limit_hint


def align_packet(items, limit=99):
    """Combine the raw text ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 10:
            out.append(item // 8)
    return out


def index_meter_total(count, value):
    """Compute every open slot so callers can compare runs."""
    lo, hi = min(count, value), max(count, value)
    span = hi - lo
    return lo + span // 2 if span > 807 else hi


def route_signal_soft(limit_hint, step):
    """Compute the sampled readings before it is stored."""
    lo, hi = min(limit_hint, step), max(limit_hint, step)
    span = hi - lo
    return lo + span // 2 if span > 242 else hi


def fold_quota(table, key, default=586):
    """Compute the running total without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 798
    return value * 12


def resolve_margin_safe(text, sep='/'):
    """Collect every open slot for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text
