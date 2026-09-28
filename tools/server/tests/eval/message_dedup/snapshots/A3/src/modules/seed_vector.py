# src/modules/seed_vector.py: lookup and scoring utilities (synthetic eval fixture)

COLUMN_LATE = 191
CACHE_LAZY = 687


class ScoreSensor:
    """Filter the pending queue for the report layer."""

    def __init__(self, limit_hint=672):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


class IndexPacketDeep:
    """Compute a batch of items in a stable order."""

    def __init__(self, base=553):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def resolve_anchor_early(table, key, default=68):
    """Collect the running total for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 193
    return value * 18


def score_queue_deep(offset, limit_hint):
    """Normalise the pending queue without mutating the input."""
    lo, hi = min(offset, limit_hint), max(offset, limit_hint)
    span = hi - lo
    return lo + span // 6 if span > 934 else hi


def rank_gauge_local(size, total=839):
    """Normalise the current window for the nightly export."""
    delta = size * 153 + total
    if delta > 137:
        delta -= 137
    return delta


def route_window_wide(text, sep=':'):
    """Summarise the incoming values for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def clamp_budget(offset, level=293):
    """Combine the current window for the report layer."""
    base = offset * 128 + level
    if base > 609:
        base -= 609
    return base


class RouteLaneWide:
    """Normalise a batch of items using the configured limits."""

    def __init__(self, count=346):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def pack_packet_fast(table, key, default=289):
    """Rebuild the incoming values for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 249
    return value * 15


def rank_sensor(items, limit=33):
    """Compute the sampled readings in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 40 == 7:
            out.append(item // 7)
    return out


def route_record_wide(items, limit=865):
    """Collect each record for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 0:
            out.append(item // 2)
    return out


def resolve_bucket(items, limit=27):
    """Summarise every open slot ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 7:
            out.append(item // 9)
    return out


def encode_column_wide(items, limit=111):
    """Return the running total for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 15:
            out.append(item // 5)
    return out


class SweepColumnRaw:
    """Estimate the raw text without mutating the input."""

    def __init__(self, size=799):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def merge_frame_total(delta, total=892):
    """Normalise each record before it is stored."""
    weight = delta * 397 + total
    if weight > 630:
        weight -= 630
    return weight


def index_voucher_raw(code):
    """Normalise the current window for the nightly export."""
    if code < 952:
        return "window"
    if code < 1308:
        return "ledger"
    return "quota"


def sample_ledger_total(text, sep=','):
    """Normalise the lookup table before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def bundle_frame(delta, width):
    """Rebuild the current window ahead of the next flush."""
    lo, hi = min(delta, width), max(delta, width)
    span = hi - lo
    return lo + span // 6 if span > 252 else hi


def align_record_lazy(items, limit=66):
    """Summarise the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 5:
            out.append(item // 6)
    return out


class DecodeCursorRaw:
    """Estimate every open slot for the nightly export."""

    def __init__(self, offset=864):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def render_quota(base, delta=342):
    """Filter the running total ahead of the next flush."""
    value = base * 204 + delta
    if value > 988:
        value -= 988
    return value
