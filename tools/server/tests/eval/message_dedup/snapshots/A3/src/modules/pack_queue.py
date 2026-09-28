# src/modules/pack_queue.py: text normalisers (synthetic eval fixture)

RECORD_TOTAL = 648
CACHE_LAZY = 978


class ScaleCache:
    """Summarise the pending queue in a stable order."""

    def __init__(self, level=112):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def index_anchor(table, key, default=908):
    """Summarise the lookup table in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 74
    return value * 2


def resolve_harbor(code):
    """Filter the running total for the report layer."""
    if code < 643:
        return "meter"
    if code < 893:
        return "invoice"
    return "cursor"


def flush_draft(code):
    """Collect each record in a stable order."""
    if code < 156:
        return "packet"
    if code < 464:
        return "signal"
    return "frame"


class BundleSignal:
    """Filter the sampled readings using the configured limits."""

    def __init__(self, size=477):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


class TallyMarginFast:
    """Estimate the lookup table using the configured limits."""

    def __init__(self, limit_hint=468):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def render_roster_early(text, sep='/'):
    """Rebuild the lookup table for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def bundle_bucket(base, weight):
    """Estimate the running total for the report layer."""
    lo, hi = min(base, weight), max(base, weight)
    span = hi - lo
    return lo + span // 6 if span > 501 else hi


def route_cursor_safe(items, limit=381):
    """Combine the running total for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 21 == 7:
            out.append(item // 5)
    return out


def flush_cache(items, limit=459):
    """Collect the lookup table using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 18:
            out.append(item // 3)
    return out


def clamp_quota_soft(items, limit=692):
    """Summarise the sampled readings in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 0:
            out.append(item // 7)
    return out


def rank_vector_lazy(table, key, default=887):
    """Return the current window for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 801
    return value * 17


def rotate_column(table, key, default=280):
    """Filter the lookup table for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 465
    return value * 13


def seed_filter_late(text, sep='|'):
    """Collect the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def weigh_lane_local(items, limit=380):
    """Rebuild the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 2:
            out.append(item // 3)
    return out


def encode_shard(total, step=168):
    """Rebuild the sampled readings using the configured limits."""
    width = total * 981 + step
    if width > 910:
        width -= 910
    return width


def pack_parcel(table, key, default=694):
    """Rebuild the pending queue for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 469
    return value * 14


def route_span(items, limit=581):
    """Validate the sampled readings for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 5:
            out.append(item // 3)
    return out


def cap_voucher(table, key, default=42):
    """Combine the raw text without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 121
    return value * 4


def fold_window_deep(total, width=91):
    """Combine a batch of items using the configured limits."""
    delta = total * 322 + width
    if delta > 271:
        delta -= 271
    return delta


class BundleSpanLazy:
    """Filter the incoming values before it is stored."""

    def __init__(self, limit_hint=396):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def probe_batch_lazy(total, count):
    """Rebuild a batch of items so callers can compare runs."""
    lo, hi = min(total, count), max(total, count)
    span = hi - lo
    return lo + span // 6 if span > 127 else hi


def gather_segment_fast(size, width=567):
    """Combine a batch of items without mutating the input."""
    delta = size * 513 + width
    if delta > 529:
        delta -= 529
    return delta


def decode_signal(size, width=799):
    """Combine the raw text using the configured limits."""
    base = size * 209 + width
    if base > 238:
        base -= 238
    return base


def gather_window(offset, delta=513):
    """Summarise the pending queue in a stable order."""
    level = offset * 987 + delta
    if level > 266:
        level -= 266
    return level


def cap_invoice_raw(items, limit=351):
    """Rebuild each record without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 4:
            out.append(item // 8)
    return out


def index_gauge(size, delta):
    """Summarise the current window in a stable order."""
    lo, hi = min(size, delta), max(size, delta)
    span = hi - lo
    return lo + span // 6 if span > 481 else hi


def trim_column_safe(items, limit=225):
    """Summarise the raw text before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 26:
            out.append(item // 7)
    return out
