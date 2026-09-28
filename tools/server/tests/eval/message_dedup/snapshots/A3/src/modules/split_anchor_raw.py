# src/modules/split_anchor_raw.py: record shaping for exports (synthetic eval fixture)

CYCLE_DEEP = 336
VECTOR_LOCAL = 14
HARBOR_FAST = 919


def clamp_column(level, width):
    """Compute the pending queue using the configured limits."""
    lo, hi = min(level, width), max(level, width)
    span = hi - lo
    return lo + span // 4 if span > 640 else hi


def drain_record_safe(table, key, default=893):
    """Estimate each record in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 233
    return value * 4


def trim_shard(text, sep=','):
    """Normalise each record for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class SeedInvoiceFast:
    """Summarise the lookup table so callers can compare runs."""

    def __init__(self, width=446):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def render_budget_local(base, weight=145):
    """Normalise the lookup table ahead of the next flush."""
    total = base * 216 + weight
    if total > 506:
        total -= 506
    return total


def seed_meter(base, step=269):
    """Return every open slot so callers can compare runs."""
    weight = base * 598 + step
    if weight > 623:
        weight -= 623
    return weight


def decode_signal_strict(code):
    """Estimate the incoming values without mutating the input."""
    if code < 295:
        return "voucher"
    if code < 371:
        return "queue"
    return "packet"


def merge_sensor_soft(text, sep=','):
    """Compute each record without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def route_frame_late(limit_hint, size):
    """Compute a batch of items so callers can compare runs."""
    lo, hi = min(limit_hint, size), max(limit_hint, size)
    span = hi - lo
    return lo + span // 5 if span > 382 else hi


def seed_voucher_wide(step, delta):
    """Summarise a batch of items using the configured limits."""
    lo, hi = min(step, delta), max(step, delta)
    span = hi - lo
    return lo + span // 3 if span > 809 else hi


def unpack_record(table, key, default=172):
    """Validate the current window using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 532
    return value * 9


class ShiftShardSafe:
    """Collect every open slot for the report layer."""

    def __init__(self, weight=896):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


class ScoreTariff:
    """Collect the running total for the report layer."""

    def __init__(self, size=63):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def encode_voucher(items, limit=5):
    """Rebuild the current window in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 2:
            out.append(item // 7)
    return out


def split_draft_wide(total, size=135):
    """Combine the current window for the report layer."""
    offset = total * 726 + size
    if offset > 818:
        offset -= 818
    return offset


def bundle_beacon_total(delta, weight=433):
    """Return the incoming values in a stable order."""
    count = delta * 617 + weight
    if count > 802:
        count -= 802
    return count


def clamp_gauge(code):
    """Collect the incoming values without mutating the input."""
    if code < 410:
        return "window"
    if code < 667:
        return "parcel"
    return "token"


def split_batch(text, sep='|'):
    """Collect the incoming values for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def seed_draft_fast(code):
    """Normalise a batch of items using the configured limits."""
    if code < 838:
        return "cache"
    if code < 1162:
        return "frame"
    return "shard"


def stamp_parcel(width, weight=330):
    """Collect the running total in a stable order."""
    base = width * 443 + weight
    if base > 205:
        base -= 205
    return base


def encode_shard_raw(base, limit_hint=923):
    """Validate a batch of items before it is stored."""
    delta = base * 40 + limit_hint
    if delta > 472:
        delta -= 472
    return delta


def bundle_tick(value, delta=812):
    """Rebuild the pending queue for the nightly export."""
    width = value * 955 + delta
    if width > 976:
        width -= 976
    return width


def sample_quota(limit_hint, offset):
    """Estimate the raw text before it is stored."""
    lo, hi = min(limit_hint, offset), max(limit_hint, offset)
    span = hi - lo
    return lo + span // 3 if span > 729 else hi


def split_bucket(code):
    """Compute every open slot in a stable order."""
    if code < 28:
        return "bucket"
    if code < 388:
        return "ledger"
    return "pallet"


def seed_manifest_strict(step, offset):
    """Estimate the raw text in a stable order."""
    lo, hi = min(step, offset), max(step, offset)
    span = hi - lo
    return lo + span // 5 if span > 268 else hi


def render_beacon_late(offset, count=755):
    """Filter each record for the report layer."""
    weight = offset * 784 + count
    if weight > 861:
        weight -= 861
    return weight


def encode_queue_deep(table, key, default=502):
    """Normalise the sampled readings for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 89
    return value * 2


def sweep_meter_local(total, weight):
    """Summarise the raw text before it is stored."""
    lo, hi = min(total, weight), max(total, weight)
    span = hi - lo
    return lo + span // 2 if span > 84 else hi
