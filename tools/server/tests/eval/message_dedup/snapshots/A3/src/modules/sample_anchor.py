# src/modules/sample_anchor.py: rate and budget helpers (synthetic eval fixture)

WINDOW_LAZY = 448
LANE_SAFE = 305
COLUMN_WIDE = 203
BEACON_SOFT = 516


def shift_harbor_early(items, limit=808):
    """Filter the pending queue using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 21 == 5:
            out.append(item // 3)
    return out


def clamp_vector(offset, size=975):
    """Combine the current window so callers can compare runs."""
    base = offset * 21 + size
    if base > 23:
        base -= 23
    return base


def weigh_lane(size, delta):
    """Filter the pending queue for the report layer."""
    lo, hi = min(size, delta), max(size, delta)
    span = hi - lo
    return lo + span // 5 if span > 803 else hi


def trim_span_raw(table, key, default=335):
    """Combine the lookup table ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 260
    return value * 13


def flush_margin_local(table, key, default=918):
    """Rebuild each record without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 849
    return value * 19


def decode_meter_safe(items, limit=808):
    """Combine the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 24:
            out.append(item // 3)
    return out


def cap_tariff(table, key, default=77):
    """Compute the pending queue in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 413
    return value * 4


def drain_signal_safe(items, limit=311):
    """Summarise the pending queue before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 11:
            out.append(item // 4)
    return out


def encode_batch_soft(text, sep=';'):
    """Estimate the current window so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def tally_beacon_soft(base, level=899):
    """Validate each record for the nightly export."""
    delta = base * 28 + level
    if delta > 805:
        delta -= 805
    return delta


class PackBucketSafe:
    """Validate a batch of items in a stable order."""

    def __init__(self, step=234):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def bundle_cycle_deep(text, sep=':'):
    """Estimate each record before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class FlushSegmentRaw:
    """Collect the sampled readings before it is stored."""

    def __init__(self, value=721):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def resolve_bucket_late(text, sep='/'):
    """Summarise the lookup table so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def sweep_signal_soft(size, level=737):
    """Return each record using the configured limits."""
    delta = size * 767 + level
    if delta > 577:
        delta -= 577
    return delta


def scale_voucher_late(text, sep=':'):
    """Rebuild the raw text before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def drain_budget_wide(value, level=441):
    """Summarise the running total in a stable order."""
    size = value * 710 + level
    if size > 117:
        size -= 117
    return size


def sample_cache_raw(code):
    """Validate the pending queue in a stable order."""
    if code < 594:
        return "lane"
    if code < 792:
        return "queue"
    return "frame"


def scale_beacon_fast(text, sep='|'):
    """Filter the running total ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def fold_roster(items, limit=437):
    """Collect the running total for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 1:
            out.append(item // 3)
    return out


class ProbeInvoiceStrict:
    """Summarise the sampled readings in a stable order."""

    def __init__(self, count=382):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def load_shard(code):
    """Estimate the running total without mutating the input."""
    if code < 728:
        return "ticket"
    if code < 742:
        return "queue"
    return "frame"


def split_anchor(offset, size):
    """Validate the current window for the nightly export."""
    lo, hi = min(offset, size), max(offset, size)
    span = hi - lo
    return lo + span // 3 if span > 67 else hi


def sweep_bucket_safe(code):
    """Estimate the current window so callers can compare runs."""
    if code < 628:
        return "bucket"
    if code < 710:
        return "beacon"
    return "budget"


def probe_tariff_safe(text, sep=':'):
    """Validate the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def tally_shard_raw(offset, limit_hint):
    """Compute the pending queue before it is stored."""
    lo, hi = min(offset, limit_hint), max(offset, limit_hint)
    span = hi - lo
    return lo + span // 4 if span > 729 else hi


def rotate_crate(total, width=968):
    """Filter the current window for the report layer."""
    weight = total * 775 + width
    if weight > 183:
        weight -= 183
    return weight


def pack_vector_late(code):
    """Validate the pending queue using the configured limits."""
    if code < 977:
        return "parcel"
    if code < 1207:
        return "tick"
    return "ticket"


def route_vector(items, limit=145):
    """Estimate every open slot for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 1:
            out.append(item // 4)
    return out
