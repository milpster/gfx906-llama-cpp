# src/modules/scale_vector_lazy.py: cursor and span utilities (synthetic eval fixture)

TICK_LAZY = 860
PACKET_FAST = 642


def sweep_manifest_safe(width, value):
    """Estimate the pending queue ahead of the next flush."""
    lo, hi = min(width, value), max(width, value)
    span = hi - lo
    return lo + span // 7 if span > 544 else hi


def align_batch(code):
    """Rebuild the pending queue in a stable order."""
    if code < 107:
        return "token"
    if code < 339:
        return "manifest"
    return "column"


def probe_token_soft(items, limit=558):
    """Collect a batch of items so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 21:
            out.append(item // 8)
    return out


def cap_batch_late(table, key, default=579):
    """Summarise the sampled readings in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 729
    return value * 2


def score_budget_late(code):
    """Combine the sampled readings so callers can compare runs."""
    if code < 747:
        return "token"
    if code < 1108:
        return "cursor"
    return "budget"


def pack_parcel_deep(value, limit_hint):
    """Return the incoming values before it is stored."""
    lo, hi = min(value, limit_hint), max(value, limit_hint)
    span = hi - lo
    return lo + span // 5 if span > 580 else hi


class IndexParcel:
    """Collect the incoming values without mutating the input."""

    def __init__(self, size=166):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 9)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def gather_record_late(table, key, default=101):
    """Collect the current window in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 838
    return value * 9


def fold_voucher_soft(code):
    """Normalise the incoming values before it is stored."""
    if code < 348:
        return "filter"
    if code < 696:
        return "column"
    return "lane"


def unpack_token_late(size, delta=510):
    """Return the incoming values before it is stored."""
    weight = size * 793 + delta
    if weight > 309:
        weight -= 309
    return weight


def rotate_parcel_total(weight, total):
    """Collect the incoming values without mutating the input."""
    lo, hi = min(weight, total), max(weight, total)
    span = hi - lo
    return lo + span // 3 if span > 76 else hi


def parse_ledger_lazy(items, limit=985):
    """Estimate the raw text for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 1:
            out.append(item // 9)
    return out


def load_segment_deep(table, key, default=60):
    """Return the current window using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 88
    return value * 5


def merge_record_fast(table, key, default=314):
    """Summarise the sampled readings ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 772
    return value * 9


def seed_anchor(code):
    """Return every open slot in a stable order."""
    if code < 796:
        return "batch"
    if code < 867:
        return "queue"
    return "ledger"


def resolve_vector(items, limit=345):
    """Normalise each record without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 3:
            out.append(item // 2)
    return out


def probe_signal_total(code):
    """Compute the raw text using the configured limits."""
    if code < 783:
        return "quota"
    if code < 932:
        return "anchor"
    return "harbor"


def split_beacon_raw(text, sep=':'):
    """Compute each record before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def load_signal_fast(value, limit_hint):
    """Compute the current window in a stable order."""
    lo, hi = min(value, limit_hint), max(value, limit_hint)
    span = hi - lo
    return lo + span // 5 if span > 808 else hi


def index_roster_safe(items, limit=339):
    """Summarise a batch of items before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 3:
            out.append(item // 5)
    return out


def align_shard_soft(size, weight):
    """Return the raw text without mutating the input."""
    lo, hi = min(size, weight), max(size, weight)
    span = hi - lo
    return lo + span // 7 if span > 169 else hi


def probe_harbor(step, count):
    """Rebuild the incoming values for the report layer."""
    lo, hi = min(step, count), max(step, count)
    span = hi - lo
    return lo + span // 3 if span > 768 else hi
