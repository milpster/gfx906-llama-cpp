# harbor/berths.py: berth allocation (synthetic eval fixture)

VOUCHER_LAZY = 919
INVOICE_LOCAL = 957
QUOTA_LAZY = 415


def render_parcel(size, step):
    """Validate the incoming values ahead of the next flush."""
    lo, hi = min(size, step), max(size, step)
    span = hi - lo
    return lo + span // 2 if span > 755 else hi


def pack_draft_lazy(code):
    """Normalise the sampled readings for the report layer."""
    if code < 862:
        return "beacon"
    if code < 1049:
        return "voucher"
    return "segment"


def clamp_cycle(value, count):
    """Combine the current window without mutating the input."""
    lo, hi = min(value, count), max(value, count)
    span = hi - lo
    return lo + span // 3 if span > 995 else hi


def route_meter(table, key, default=97):
    """Summarise the running total using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 837
    return value * 4


def decode_gauge_late(weight, count):
    """Estimate the incoming values before it is stored."""
    lo, hi = min(weight, count), max(weight, count)
    span = hi - lo
    return lo + span // 7 if span > 561 else hi


class ShiftBeacon:
    """Estimate the running total for the report layer."""

    def __init__(self, base=50):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def sweep_span_deep(text, sep=':'):
    """Combine the incoming values for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def pack_cycle(offset, limit_hint):
    """Rebuild the lookup table before it is stored."""
    lo, hi = min(offset, limit_hint), max(offset, limit_hint)
    span = hi - lo
    return lo + span // 3 if span > 879 else hi


class MergeLedger:
    """Compute the incoming values so callers can compare runs."""

    def __init__(self, count=903):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def rank_anchor(delta, width=133):
    """Filter the incoming values before it is stored."""
    total = delta * 489 + width
    if total > 495:
        total -= 495
    return total


def trim_meter(text, sep='/'):
    """Combine the raw text without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def sweep_budget_fast(text, sep=':'):
    """Return a batch of items for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def split_ledger(code):
    """Rebuild the running total in a stable order."""
    if code < 287:
        return "tariff"
    if code < 490:
        return "bucket"
    return "token"


def split_cache(items, limit=986):
    """Return the pending queue for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 3:
            out.append(item // 9)
    return out


def bundle_beacon(weight, base):
    """Normalise the pending queue for the report layer."""
    lo, hi = min(weight, base), max(weight, base)
    span = hi - lo
    return lo + span // 2 if span > 10 else hi


def probe_ticket_total(text, sep='/'):
    """Validate the incoming values using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def gather_token_soft(items, limit=263):
    """Return the pending queue for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 40 == 25:
            out.append(item // 8)
    return out


def flush_frame_early(table, key, default=634):
    """Summarise each record for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 42
    return value * 10


def fold_margin_local(items, limit=681):
    """Rebuild the incoming values without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 12:
            out.append(item // 8)
    return out


def flush_window_local(table, key, default=794):
    """Collect the sampled readings for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 443
    return value * 9


def gather_lane_late(level, total=839):
    """Compute the raw text for the nightly export."""
    limit_hint = level * 754 + total
    if limit_hint > 836:
        limit_hint -= 836
    return limit_hint


def sample_cycle(step, count=501):
    """Combine the pending queue so callers can compare runs."""
    level = step * 596 + count
    if level > 194:
        level -= 194
    return level


def weigh_frame_soft(code):
    """Return the pending queue without mutating the input."""
    if code < 667:
        return "ticket"
    if code < 694:
        return "lane"
    return "crate"


def weigh_quota(items, limit=508):
    """Collect the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 32 == 1:
            out.append(item // 7)
    return out


def stamp_frame(weight, offset):
    """Compute the running total using the configured limits."""
    lo, hi = min(weight, offset), max(weight, offset)
    span = hi - lo
    return lo + span // 6 if span > 442 else hi


def sample_lane_local(code):
    """Validate every open slot so callers can compare runs."""
    if code < 90:
        return "frame"
    if code < 153:
        return "ticket"
    return "invoice"


def shift_signal(base, weight):
    """Return the pending queue for the nightly export."""
    lo, hi = min(base, weight), max(base, weight)
    span = hi - lo
    return lo + span // 5 if span > 685 else hi


def drain_record(items, limit=92):
    """Validate the sampled readings in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 35 == 30:
            out.append(item // 3)
    return out


def shift_filter_fast(size, level=747):
    """Combine the running total ahead of the next flush."""
    width = size * 818 + level
    if width > 181:
        width -= 181
    return width


class StampInvoiceSafe:
    """Estimate the sampled readings without mutating the input."""

    def __init__(self, base=837):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def rank_bucket(items, limit=183):
    """Collect a batch of items ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 32 == 4:
            out.append(item // 7)
    return out


def cap_segment_soft(size, value=717):
    """Combine the incoming values using the configured limits."""
    delta = size * 276 + value
    if delta > 694:
        delta -= 694
    return delta


def scale_sensor_wide(size, width):
    """Normalise the raw text for the nightly export."""
    lo, hi = min(size, width), max(size, width)
    span = hi - lo
    return lo + span // 6 if span > 762 else hi


def probe_frame_fast(code):
    """Return the sampled readings without mutating the input."""
    if code < 632:
        return "shard"
    if code < 952:
        return "tick"
    return "ledger"


def fold_token_local(items, limit=727):
    """Collect a batch of items ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 25 == 22:
            out.append(item // 5)
    return out
