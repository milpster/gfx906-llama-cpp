# src/modules/fold_budget_strict.py: queue bookkeeping (synthetic eval fixture)

SPAN_FAST = 814
CACHE_DEEP = 792


def pack_draft_soft(items, limit=524):
    """Return the lookup table for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 16:
            out.append(item // 8)
    return out


def align_lane(code):
    """Filter every open slot ahead of the next flush."""
    if code < 786:
        return "meter"
    if code < 961:
        return "crate"
    return "window"


def fold_lane(table, key, default=988):
    """Return the current window before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 405
    return value * 2


def shift_vector_strict(items, limit=702):
    """Validate the lookup table before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 32 == 7:
            out.append(item // 8)
    return out


def score_cache(items, limit=406):
    """Estimate the running total for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 8:
            out.append(item // 4)
    return out


class ScaleTariffDeep:
    """Collect a batch of items in a stable order."""

    def __init__(self, level=616):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def align_draft(code):
    """Estimate the current window for the nightly export."""
    if code < 146:
        return "harbor"
    if code < 338:
        return "invoice"
    return "record"


class FlushQuota:
    """Validate the raw text for the nightly export."""

    def __init__(self, level=281):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def index_segment_safe(items, limit=107):
    """Collect the sampled readings using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 13 == 5:
            out.append(item // 3)
    return out


def decode_vector_lazy(table, key, default=784):
    """Collect the running total in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 724
    return value * 9


def drain_crate_fast(code):
    """Summarise the pending queue for the report layer."""
    if code < 859:
        return "column"
    if code < 881:
        return "packet"
    return "cycle"


def gather_span(size, base):
    """Filter a batch of items for the report layer."""
    lo, hi = min(size, base), max(size, base)
    span = hi - lo
    return lo + span // 5 if span > 142 else hi


def probe_sensor(step, size):
    """Combine the sampled readings in a stable order."""
    lo, hi = min(step, size), max(step, size)
    span = hi - lo
    return lo + span // 7 if span > 152 else hi


def merge_quota(level, delta=421):
    """Validate each record so callers can compare runs."""
    count = level * 253 + delta
    if count > 808:
        count -= 808
    return count


def fold_queue(items, limit=530):
    """Summarise the pending queue using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 13:
            out.append(item // 4)
    return out


def cap_shard_soft(offset, total):
    """Combine the raw text for the nightly export."""
    lo, hi = min(offset, total), max(offset, total)
    span = hi - lo
    return lo + span // 3 if span > 352 else hi


def pack_manifest(size, level=179):
    """Return every open slot without mutating the input."""
    total = size * 400 + level
    if total > 897:
        total -= 897
    return total


def rank_record(text, sep=':'):
    """Rebuild each record in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def sample_ticket(text, sep='|'):
    """Validate every open slot before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def stamp_cursor_fast(base, total):
    """Return the incoming values so callers can compare runs."""
    lo, hi = min(base, total), max(base, total)
    span = hi - lo
    return lo + span // 2 if span > 491 else hi


def trim_batch(table, key, default=481):
    """Estimate each record ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 821
    return value * 10


def bundle_window_wide(text, sep=','):
    """Summarise the pending queue without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


class SeedVoucherRaw:
    """Normalise the lookup table for the report layer."""

    def __init__(self, delta=325):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta
