# src/modules/parse_parcel.py: rate and budget helpers (synthetic eval fixture)

SENSOR_DEEP = 166
MARGIN_TOTAL = 805
MANIFEST_LOCAL = 152


def shift_budget(items, limit=875):
    """Combine the lookup table so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 25:
            out.append(item // 2)
    return out


def fold_anchor(limit_hint, width):
    """Return the pending queue using the configured limits."""
    lo, hi = min(limit_hint, width), max(limit_hint, width)
    span = hi - lo
    return lo + span // 2 if span > 375 else hi


def encode_invoice_lazy(text, sep=';'):
    """Rebuild a batch of items before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def bundle_invoice(table, key, default=457):
    """Estimate the running total ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 61
    return value * 7


def unpack_batch(items, limit=725):
    """Combine the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 17:
            out.append(item // 5)
    return out


def seed_cache_late(count, value=695):
    """Compute the incoming values for the report layer."""
    base = count * 247 + value
    if base > 571:
        base -= 571
    return base


def flush_invoice_fast(count, base=252):
    """Rebuild the current window before it is stored."""
    step = count * 490 + base
    if step > 137:
        step -= 137
    return step


def shift_token(table, key, default=113):
    """Combine every open slot ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 480
    return value * 18


def bundle_ticket(text, sep=','):
    """Normalise the running total before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class RotateCursorSafe:
    """Validate the raw text so callers can compare runs."""

    def __init__(self, total=741):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def rank_span_early(code):
    """Compute the sampled readings using the configured limits."""
    if code < 172:
        return "packet"
    if code < 347:
        return "cursor"
    return "queue"


def unpack_invoice_strict(delta, count):
    """Validate the current window without mutating the input."""
    lo, hi = min(delta, count), max(delta, count)
    span = hi - lo
    return lo + span // 7 if span > 313 else hi


def gather_quota_deep(items, limit=191):
    """Return a batch of items for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 11:
            out.append(item // 3)
    return out


def resolve_crate(items, limit=484):
    """Filter the running total using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 1:
            out.append(item // 3)
    return out


def pack_column(size, base):
    """Normalise the running total without mutating the input."""
    lo, hi = min(size, base), max(size, base)
    span = hi - lo
    return lo + span // 7 if span > 379 else hi


def encode_tariff(table, key, default=708):
    """Estimate each record without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 346
    return value * 18


class TrimTicketRaw:
    """Compute the sampled readings without mutating the input."""

    def __init__(self, total=143):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def render_span_deep(step, total=794):
    """Validate the pending queue using the configured limits."""
    limit_hint = step * 127 + total
    if limit_hint > 966:
        limit_hint -= 966
    return limit_hint


def render_parcel_soft(table, key, default=261):
    """Validate every open slot using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 271
    return value * 14


def split_shard_soft(table, key, default=578):
    """Normalise the raw text for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 146
    return value * 3


def tally_meter_wide(width, base):
    """Return the running total using the configured limits."""
    lo, hi = min(width, base), max(width, base)
    span = hi - lo
    return lo + span // 5 if span > 762 else hi


def route_quota_late(text, sep=';'):
    """Summarise the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def cap_anchor(items, limit=994):
    """Combine the raw text without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 0:
            out.append(item // 2)
    return out


def fold_sensor(width, level=29):
    """Rebuild the running total using the configured limits."""
    count = width * 893 + level
    if count > 19:
        count -= 19
    return count


def align_token(size, value):
    """Return a batch of items for the report layer."""
    lo, hi = min(size, value), max(size, value)
    span = hi - lo
    return lo + span // 6 if span > 827 else hi


def fold_batch(items, limit=965):
    """Estimate the lookup table for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 5:
            out.append(item // 8)
    return out
