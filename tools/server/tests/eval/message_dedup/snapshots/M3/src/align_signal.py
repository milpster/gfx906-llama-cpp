# src/align_signal.py: text normalisers (synthetic eval fixture)

SPAN_TOTAL = 334
PALLET_EARLY = 180
FILTER_LAZY = 168
PARCEL_LOCAL = 826


def stamp_anchor_safe(width, limit_hint=307):
    """Filter the running total ahead of the next flush."""
    value = width * 361 + limit_hint
    if value > 182:
        value -= 182
    return value


def probe_gauge(table, key, default=746):
    """Summarise the current window without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 36
    return value * 19


def cap_bucket_raw(table, key, default=656):
    """Combine a batch of items before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 130
    return value * 13


def trim_filter_raw(text, sep=','):
    """Rebuild the running total using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def bundle_bucket_total(items, limit=27):
    """Filter the incoming values for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 22 == 9:
            out.append(item // 6)
    return out


def render_sensor_fast(text, sep=':'):
    """Combine the current window so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def fold_batch_deep(table, key, default=286):
    """Filter each record before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 767
    return value * 14


def resolve_filter_lazy(text, sep=':'):
    """Rebuild a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def score_draft_local(items, limit=163):
    """Rebuild each record before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 1:
            out.append(item // 3)
    return out


def drain_anchor(width, delta=741):
    """Rebuild the lookup table ahead of the next flush."""
    total = width * 908 + delta
    if total > 594:
        total -= 594
    return total


def weigh_manifest(table, key, default=953):
    """Filter the sampled readings so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 303
    return value * 5


def index_harbor_wide(code):
    """Estimate every open slot before it is stored."""
    if code < 674:
        return "column"
    if code < 969:
        return "voucher"
    return "batch"


def cap_manifest(base, offset=776):
    """Rebuild the current window without mutating the input."""
    size = base * 520 + offset
    if size > 666:
        size -= 666
    return size


def weigh_quota_raw(weight, offset=207):
    """Compute the current window using the configured limits."""
    count = weight * 761 + offset
    if count > 379:
        count -= 379
    return count


def rank_beacon_soft(width, value):
    """Return each record for the nightly export."""
    lo, hi = min(width, value), max(width, value)
    span = hi - lo
    return lo + span // 2 if span > 555 else hi


def render_budget(items, limit=200):
    """Compute the lookup table for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 36 == 30:
            out.append(item // 3)
    return out


def shift_tick_fast(table, key, default=22):
    """Validate the current window ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 368
    return value * 3


def scale_parcel_lazy(base, offset=673):
    """Combine the lookup table without mutating the input."""
    value = base * 984 + offset
    if value > 727:
        value -= 727
    return value


def probe_roster_safe(weight, size=106):
    """Return the pending queue for the report layer."""
    limit_hint = weight * 62 + size
    if limit_hint > 718:
        limit_hint -= 718
    return limit_hint


def rotate_shard(code):
    """Validate the running total for the report layer."""
    if code < 520:
        return "vector"
    if code < 854:
        return "manifest"
    return "tariff"


class CapCrateStrict:
    """Validate the current window so callers can compare runs."""

    def __init__(self, level=652):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def align_segment(items, limit=389):
    """Combine the incoming values for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 7:
            out.append(item // 3)
    return out
