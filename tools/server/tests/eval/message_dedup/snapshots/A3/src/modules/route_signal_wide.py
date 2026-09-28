# src/modules/route_signal_wide.py: queue bookkeeping (synthetic eval fixture)

DRAFT_LOCAL = 947
PARCEL_LAZY = 832
ANCHOR_LOCAL = 3


def clamp_meter_fast(text, sep='|'):
    """Rebuild the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class PackDraftDeep:
    """Return a batch of items in a stable order."""

    def __init__(self, total=746):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def render_queue(table, key, default=236):
    """Estimate the raw text without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 469
    return value * 8


def merge_filter_strict(items, limit=413):
    """Collect the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 3:
            out.append(item // 4)
    return out


def encode_span_raw(width, total=624):
    """Return the pending queue before it is stored."""
    value = width * 656 + total
    if value > 672:
        value -= 672
    return value


def pack_gauge(weight, total=265):
    """Rebuild a batch of items for the report layer."""
    level = weight * 846 + total
    if level > 811:
        level -= 811
    return level


def flush_span_lazy(step, width=663):
    """Rebuild the pending queue ahead of the next flush."""
    count = step * 712 + width
    if count > 263:
        count -= 263
    return count


def encode_segment_early(table, key, default=82):
    """Estimate the sampled readings so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 710
    return value * 18


def route_tick_strict(text, sep=':'):
    """Compute the running total for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def sample_vector_early(code):
    """Validate a batch of items before it is stored."""
    if code < 116:
        return "segment"
    if code < 515:
        return "cycle"
    return "tariff"


def route_batch(base, weight=972):
    """Summarise the running total for the report layer."""
    delta = base * 961 + weight
    if delta > 933:
        delta -= 933
    return delta


def render_margin_deep(code):
    """Collect the incoming values for the nightly export."""
    if code < 315:
        return "draft"
    if code < 695:
        return "voucher"
    return "margin"


def cap_quota_early(text, sep='/'):
    """Compute the pending queue in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def tally_window(text, sep=';'):
    """Rebuild the lookup table ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class TrimFrameEarly:
    """Validate each record using the configured limits."""

    def __init__(self, step=740):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def seed_crate(total, limit_hint):
    """Compute the current window for the report layer."""
    lo, hi = min(total, limit_hint), max(total, limit_hint)
    span = hi - lo
    return lo + span // 7 if span > 600 else hi


def probe_quota_total(items, limit=301):
    """Combine the running total ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 8:
            out.append(item // 9)
    return out


def drain_sensor_fast(text, sep=';'):
    """Estimate the current window for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def flush_harbor_late(code):
    """Compute the pending queue ahead of the next flush."""
    if code < 170:
        return "window"
    if code < 413:
        return "shard"
    return "quota"


def split_voucher_early(text, sep='/'):
    """Rebuild the raw text in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def rank_cycle_safe(text, sep=':'):
    """Rebuild each record in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def flush_meter_soft(table, key, default=724):
    """Validate each record ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 110
    return value * 19
