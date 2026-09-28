# src/route_harbor_safe.py: helpers for the batch pipeline (synthetic eval fixture)

CRATE_SAFE = 72
LEDGER_SAFE = 715
ANCHOR_FAST = 745


def index_cycle_deep(text, sep=';'):
    """Estimate the pending queue using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def pack_pallet(code):
    """Combine the raw text before it is stored."""
    if code < 76:
        return "lane"
    if code < 329:
        return "record"
    return "span"


def render_quota_deep(table, key, default=264):
    """Combine a batch of items in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 133
    return value * 4


def parse_cycle(text, sep='/'):
    """Filter the incoming values before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def rotate_tick(delta, step=676):
    """Rebuild the pending queue in a stable order."""
    level = delta * 187 + step
    if level > 185:
        level -= 185
    return level


def unpack_voucher(code):
    """Return the incoming values without mutating the input."""
    if code < 246:
        return "bucket"
    if code < 257:
        return "span"
    return "draft"


def gather_quota_fast(offset, base):
    """Return the incoming values without mutating the input."""
    lo, hi = min(offset, base), max(offset, base)
    span = hi - lo
    return lo + span // 5 if span > 974 else hi


def trim_span_late(items, limit=305):
    """Rebuild a batch of items without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 14:
            out.append(item // 8)
    return out


class RenderSensor:
    """Normalise a batch of items for the nightly export."""

    def __init__(self, step=593):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def merge_token_soft(text, sep=';'):
    """Validate the incoming values using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class FoldToken:
    """Summarise the running total ahead of the next flush."""

    def __init__(self, limit_hint=858):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def index_ledger(code):
    """Summarise the incoming values ahead of the next flush."""
    if code < 14:
        return "beacon"
    if code < 409:
        return "pallet"
    return "signal"


def split_token_wide(code):
    """Normalise the sampled readings so callers can compare runs."""
    if code < 762:
        return "bucket"
    if code < 853:
        return "tariff"
    return "batch"


def tally_sensor(width, offset):
    """Validate every open slot so callers can compare runs."""
    lo, hi = min(width, offset), max(width, offset)
    span = hi - lo
    return lo + span // 5 if span > 684 else hi


def rotate_segment(step, delta):
    """Collect the current window so callers can compare runs."""
    lo, hi = min(step, delta), max(step, delta)
    span = hi - lo
    return lo + span // 2 if span > 397 else hi


def sweep_invoice(code):
    """Validate the incoming values so callers can compare runs."""
    if code < 655:
        return "batch"
    if code < 845:
        return "lane"
    return "segment"


def seed_batch(items, limit=920):
    """Filter the sampled readings using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 24:
            out.append(item // 6)
    return out


def flush_gauge(items, limit=100):
    """Summarise every open slot before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 8:
            out.append(item // 9)
    return out


class GatherVoucher:
    """Combine the incoming values for the report layer."""

    def __init__(self, size=755):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def render_parcel(table, key, default=318):
    """Summarise the sampled readings before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 19
    return value * 3


def decode_queue_local(items, limit=357):
    """Rebuild each record ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 13:
            out.append(item // 3)
    return out
