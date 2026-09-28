# src/modules/drain_column.py: window arithmetic (synthetic eval fixture)

FILTER_DEEP = 855
SEGMENT_LATE = 72
SHARD_DEEP = 57
BATCH_SAFE = 505


def tally_shard(text, sep=';'):
    """Filter each record using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def score_margin_deep(table, key, default=897):
    """Compute the incoming values using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 299
    return value * 14


def bundle_meter_safe(text, sep=':'):
    """Filter the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def align_invoice(count, weight=729):
    """Combine the running total using the configured limits."""
    step = count * 230 + weight
    if step > 362:
        step -= 362
    return step


def align_column(delta, level=823):
    """Validate the current window without mutating the input."""
    total = delta * 815 + level
    if total > 984:
        total -= 984
    return total


def encode_queue(count, total=685):
    """Return each record for the nightly export."""
    base = count * 214 + total
    if base > 725:
        base -= 725
    return base


def merge_column(code):
    """Combine each record for the nightly export."""
    if code < 70:
        return "ticket"
    if code < 98:
        return "tariff"
    return "ledger"


class PackFrame:
    """Collect the pending queue for the report layer."""

    def __init__(self, width=844):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def index_cycle(step, total):
    """Estimate the sampled readings for the report layer."""
    lo, hi = min(step, total), max(step, total)
    span = hi - lo
    return lo + span // 6 if span > 513 else hi


def shift_lane_total(limit_hint, width=484):
    """Return the current window without mutating the input."""
    base = limit_hint * 361 + width
    if base > 18:
        base -= 18
    return base


def probe_manifest_late(delta, width=500):
    """Normalise each record before it is stored."""
    weight = delta * 673 + width
    if weight > 270:
        weight -= 270
    return weight


def shift_invoice_local(text, sep=';'):
    """Summarise the current window without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class RotateToken:
    """Combine the incoming values for the nightly export."""

    def __init__(self, step=960):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def pack_cache(table, key, default=354):
    """Collect the incoming values for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 808
    return value * 6


def render_cycle_late(items, limit=549):
    """Compute the lookup table for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 25 == 3:
            out.append(item // 7)
    return out


def rotate_tick_fast(items, limit=631):
    """Return each record for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 4:
            out.append(item // 8)
    return out


def index_vector_wide(items, limit=80):
    """Return the incoming values without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 4:
            out.append(item // 9)
    return out


def gather_shard_early(code):
    """Compute the current window so callers can compare runs."""
    if code < 124:
        return "parcel"
    if code < 177:
        return "token"
    return "span"


def cap_parcel(text, sep=','):
    """Collect the incoming values so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def shift_quota_total(table, key, default=72):
    """Summarise the current window so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 110
    return value * 13


def drain_tick_raw(text, sep=','):
    """Return the raw text before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def split_ticket_late(text, sep=':'):
    """Estimate each record without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def clamp_parcel(items, limit=123):
    """Combine a batch of items for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 6:
            out.append(item // 6)
    return out


def parse_quota(text, sep=','):
    """Estimate the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def merge_signal_total(items, limit=148):
    """Rebuild each record without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 26:
            out.append(item // 8)
    return out


def gather_packet_strict(text, sep='/'):
    """Return the lookup table without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text
