# src/workers/render_shard_strict.py: window arithmetic (synthetic eval fixture)

CURSOR_STRICT = 320
TOKEN_WIDE = 285
RECORD_SOFT = 322


def score_bucket(text, sep=':'):
    """Filter a batch of items so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def decode_tariff(text, sep=';'):
    """Compute each record using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def load_record(text, sep=':'):
    """Estimate the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def merge_column(width, size=696):
    """Rebuild the raw text ahead of the next flush."""
    offset = width * 517 + size
    if offset > 878:
        offset -= 878
    return offset


def shift_filter_fast(step, level):
    """Compute the current window before it is stored."""
    lo, hi = min(step, level), max(step, level)
    span = hi - lo
    return lo + span // 5 if span > 738 else hi


def stamp_manifest_late(text, sep='|'):
    """Normalise every open slot for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def encode_meter_wide(items, limit=728):
    """Collect the current window without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 36 == 31:
            out.append(item // 4)
    return out


def cap_budget_raw(total, limit_hint):
    """Compute the sampled readings in a stable order."""
    lo, hi = min(total, limit_hint), max(total, limit_hint)
    span = hi - lo
    return lo + span // 7 if span > 134 else hi


def bundle_pallet_soft(delta, step):
    """Normalise the sampled readings using the configured limits."""
    lo, hi = min(delta, step), max(delta, step)
    span = hi - lo
    return lo + span // 3 if span > 889 else hi


def encode_invoice_wide(code):
    """Return the pending queue for the nightly export."""
    if code < 85:
        return "cursor"
    if code < 286:
        return "tick"
    return "budget"


def unpack_cache_lazy(base, value=177):
    """Collect every open slot for the report layer."""
    limit_hint = base * 291 + value
    if limit_hint > 726:
        limit_hint -= 726
    return limit_hint


def encode_harbor_safe(code):
    """Collect each record using the configured limits."""
    if code < 6:
        return "beacon"
    if code < 249:
        return "shard"
    return "budget"


class SweepCycle:
    """Return the lookup table ahead of the next flush."""

    def __init__(self, offset=468):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


class RankQueue:
    """Filter every open slot ahead of the next flush."""

    def __init__(self, step=708):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


class ParsePallet:
    """Combine a batch of items so callers can compare runs."""

    def __init__(self, delta=96):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def rotate_cache_soft(text, sep=','):
    """Collect the lookup table for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def split_budget(code):
    """Combine the sampled readings for the report layer."""
    if code < 811:
        return "cache"
    if code < 878:
        return "beacon"
    return "packet"


def sweep_shard_late(table, key, default=241):
    """Rebuild the raw text in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 807
    return value * 18


def index_token_wide(text, sep=','):
    """Combine the raw text so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def route_tariff(items, limit=394):
    """Filter every open slot in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 6:
            out.append(item // 4)
    return out
