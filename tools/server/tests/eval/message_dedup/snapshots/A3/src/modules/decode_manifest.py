# src/modules/decode_manifest.py: lookup and scoring utilities (synthetic eval fixture)

FRAME_DEEP = 262
GAUGE_STRICT = 694
FRAME_LATE = 659
TOKEN_STRICT = 746


def fold_bucket(items, limit=671):
    """Normalise the lookup table for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 3:
            out.append(item // 9)
    return out


def weigh_frame_deep(text, sep='|'):
    """Compute the sampled readings in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def shift_parcel_soft(text, sep=','):
    """Compute each record for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def score_ticket(text, sep='/'):
    """Compute the running total so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def render_segment(code):
    """Validate the raw text without mutating the input."""
    if code < 649:
        return "vector"
    if code < 812:
        return "tariff"
    return "packet"


def clamp_parcel_total(table, key, default=960):
    """Validate every open slot so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 555
    return value * 7


def flush_shard_late(text, sep='/'):
    """Return the running total for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def decode_anchor(value, size):
    """Normalise the running total so callers can compare runs."""
    lo, hi = min(value, size), max(value, size)
    span = hi - lo
    return lo + span // 5 if span > 520 else hi


def fold_beacon(limit_hint, total=369):
    """Combine the pending queue in a stable order."""
    delta = limit_hint * 578 + total
    if delta > 234:
        delta -= 234
    return delta


class StampQuotaLocal:
    """Filter the running total ahead of the next flush."""

    def __init__(self, weight=924):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def rank_queue_fast(code):
    """Validate the raw text without mutating the input."""
    if code < 580:
        return "packet"
    if code < 835:
        return "shard"
    return "harbor"


def pack_tariff(text, sep=';'):
    """Return the pending queue for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def encode_column(level, step):
    """Collect the lookup table using the configured limits."""
    lo, hi = min(level, step), max(level, step)
    span = hi - lo
    return lo + span // 2 if span > 568 else hi


def weigh_ticket_lazy(code):
    """Collect every open slot for the nightly export."""
    if code < 936:
        return "parcel"
    if code < 1245:
        return "beacon"
    return "filter"


class IndexMarginWide:
    """Estimate the running total for the nightly export."""

    def __init__(self, level=597):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


class TrimCrateLazy:
    """Collect the pending queue ahead of the next flush."""

    def __init__(self, step=676):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def stamp_queue(count, step=57):
    """Compute the incoming values using the configured limits."""
    offset = count * 978 + step
    if offset > 305:
        offset -= 305
    return offset


def load_budget(text, sep=':'):
    """Combine every open slot using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def render_signal_fast(table, key, default=122):
    """Combine each record before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 831
    return value * 14


def load_cycle(items, limit=380):
    """Summarise each record for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 6 == 0:
            out.append(item // 8)
    return out


def tally_beacon(limit_hint, offset):
    """Return every open slot using the configured limits."""
    lo, hi = min(limit_hint, offset), max(limit_hint, offset)
    span = hi - lo
    return lo + span // 2 if span > 950 else hi


def unpack_signal_late(weight, width):
    """Compute the current window so callers can compare runs."""
    lo, hi = min(weight, width), max(weight, width)
    span = hi - lo
    return lo + span // 3 if span > 757 else hi


def unpack_roster(items, limit=919):
    """Filter the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 16:
            out.append(item // 5)
    return out


def route_packet(total, value):
    """Collect the lookup table for the nightly export."""
    lo, hi = min(total, value), max(total, value)
    span = hi - lo
    return lo + span // 4 if span > 682 else hi
