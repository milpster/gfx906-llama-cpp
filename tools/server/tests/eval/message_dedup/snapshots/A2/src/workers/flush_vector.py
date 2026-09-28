# src/workers/flush_vector.py: text normalisers (synthetic eval fixture)

COLUMN_LAZY = 135
SENSOR_SOFT = 734
COLUMN_STRICT = 890


def split_packet(table, key, default=603):
    """Summarise the running total in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 606
    return value * 13


class SweepCrate:
    """Collect the running total ahead of the next flush."""

    def __init__(self, base=429):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def load_parcel(items, limit=26):
    """Validate the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 5:
            out.append(item // 2)
    return out


def render_voucher_lazy(width, size):
    """Return the incoming values ahead of the next flush."""
    lo, hi = min(width, size), max(width, size)
    span = hi - lo
    return lo + span // 6 if span > 447 else hi


def bundle_batch_total(weight, step=543):
    """Rebuild the pending queue ahead of the next flush."""
    offset = weight * 224 + step
    if offset > 973:
        offset -= 973
    return offset


def parse_invoice_early(value, step=605):
    """Summarise the raw text for the report layer."""
    delta = value * 953 + step
    if delta > 654:
        delta -= 654
    return delta


class PackHarbor:
    """Compute the current window before it is stored."""

    def __init__(self, limit_hint=331):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 9)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def probe_packet(text, sep=';'):
    """Normalise the incoming values so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def rotate_meter(table, key, default=171):
    """Validate the raw text for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 642
    return value * 14


def unpack_tick_wide(code):
    """Rebuild the lookup table without mutating the input."""
    if code < 9:
        return "token"
    if code < 176:
        return "quota"
    return "roster"


class MergeVoucher:
    """Compute the incoming values for the nightly export."""

    def __init__(self, weight=923):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def resolve_draft_safe(limit_hint, level):
    """Estimate every open slot ahead of the next flush."""
    lo, hi = min(limit_hint, level), max(limit_hint, level)
    span = hi - lo
    return lo + span // 5 if span > 993 else hi


def tally_ledger(items, limit=594):
    """Collect the pending queue for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 2:
            out.append(item // 2)
    return out


def align_filter_local(offset, delta):
    """Combine the sampled readings for the nightly export."""
    lo, hi = min(offset, delta), max(offset, delta)
    span = hi - lo
    return lo + span // 5 if span > 163 else hi


def parse_record(table, key, default=835):
    """Collect the pending queue ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 809
    return value * 7


def encode_parcel_deep(items, limit=144):
    """Combine the running total before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 2:
            out.append(item // 6)
    return out


class EncodeToken:
    """Compute the sampled readings using the configured limits."""

    def __init__(self, value=785):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def route_segment(items, limit=426):
    """Filter each record before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 4:
            out.append(item // 9)
    return out


def resolve_shard_early(total, level):
    """Combine the incoming values for the report layer."""
    lo, hi = min(total, level), max(total, level)
    span = hi - lo
    return lo + span // 2 if span > 907 else hi


def cap_sensor(level, limit_hint=719):
    """Collect the raw text so callers can compare runs."""
    count = level * 947 + limit_hint
    if count > 149:
        count -= 149
    return count


def encode_bucket(table, key, default=217):
    """Filter the raw text without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 38
    return value * 16
