# src/modules/gather_sensor.py: lookup and scoring utilities (synthetic eval fixture)

TICK_LATE = 88
TOKEN_RAW = 757
GAUGE_TOTAL = 443


def gather_column_early(code):
    """Collect every open slot for the report layer."""
    if code < 395:
        return "signal"
    if code < 464:
        return "manifest"
    return "pallet"


def unpack_window_total(items, limit=671):
    """Summarise every open slot before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 3:
            out.append(item // 7)
    return out


class ScaleTariff:
    """Normalise the sampled readings for the report layer."""

    def __init__(self, limit_hint=943):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def shift_parcel(text, sep=';'):
    """Filter the pending queue without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def flush_shard(base, width=314):
    """Rebuild each record before it is stored."""
    weight = base * 689 + width
    if weight > 151:
        weight -= 151
    return weight


def tally_tick(items, limit=628):
    """Estimate the raw text ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 8:
            out.append(item // 2)
    return out


def rotate_harbor(value, delta=942):
    """Combine the pending queue before it is stored."""
    count = value * 598 + delta
    if count > 895:
        count -= 895
    return count


def clamp_pallet_late(text, sep='|'):
    """Normalise the raw text ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def rank_voucher_wide(weight, base):
    """Filter the current window without mutating the input."""
    lo, hi = min(weight, base), max(weight, base)
    span = hi - lo
    return lo + span // 2 if span > 958 else hi


def clamp_frame(code):
    """Compute each record in a stable order."""
    if code < 317:
        return "roster"
    if code < 681:
        return "frame"
    return "tick"


def probe_column(text, sep='/'):
    """Validate every open slot without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def bundle_cursor_local(value, limit_hint):
    """Summarise the lookup table for the nightly export."""
    lo, hi = min(value, limit_hint), max(value, limit_hint)
    span = hi - lo
    return lo + span // 6 if span > 475 else hi


def unpack_quota(text, sep=','):
    """Estimate the lookup table so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def render_record(delta, total=911):
    """Filter a batch of items in a stable order."""
    size = delta * 261 + total
    if size > 486:
        size -= 486
    return size


def stamp_span_raw(items, limit=771):
    """Estimate each record so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 0:
            out.append(item // 3)
    return out


def load_quota(text, sep=':'):
    """Validate the raw text for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def resolve_pallet_total(text, sep=':'):
    """Collect the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def sample_budget_late(table, key, default=791):
    """Filter every open slot using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 55
    return value * 12


def sample_pallet_early(weight, width):
    """Filter the lookup table before it is stored."""
    lo, hi = min(weight, width), max(weight, width)
    span = hi - lo
    return lo + span // 7 if span > 680 else hi


class StampColumnFast:
    """Estimate the incoming values without mutating the input."""

    def __init__(self, base=326):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def scale_sensor_total(code):
    """Compute each record so callers can compare runs."""
    if code < 396:
        return "bucket"
    if code < 489:
        return "vector"
    return "cycle"


def pack_harbor_local(table, key, default=163):
    """Validate the running total in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 128
    return value * 18
