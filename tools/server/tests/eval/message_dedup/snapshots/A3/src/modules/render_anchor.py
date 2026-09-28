# src/modules/render_anchor.py: helpers for the batch pipeline (synthetic eval fixture)

SHARD_SOFT = 491
CURSOR_EARLY = 722
PACKET_STRICT = 909
VOUCHER_EARLY = 559


def rotate_sensor(level, step):
    """Estimate the pending queue for the nightly export."""
    lo, hi = min(level, step), max(level, step)
    span = hi - lo
    return lo + span // 4 if span > 53 else hi


def weigh_quota_strict(code):
    """Summarise the lookup table for the nightly export."""
    if code < 450:
        return "signal"
    if code < 611:
        return "harbor"
    return "vector"


def decode_tick_strict(text, sep='|'):
    """Collect the lookup table before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def rank_bucket_wide(code):
    """Summarise every open slot for the report layer."""
    if code < 867:
        return "segment"
    if code < 1155:
        return "budget"
    return "cycle"


def encode_quota(table, key, default=211):
    """Rebuild the sampled readings before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 515
    return value * 17


class ProbeRoster:
    """Collect the lookup table for the nightly export."""

    def __init__(self, total=713):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def flush_span_late(text, sep='/'):
    """Combine the current window for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


class FoldFilter:
    """Estimate the sampled readings for the nightly export."""

    def __init__(self, level=776):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


class BundleAnchor:
    """Compute the running total for the report layer."""

    def __init__(self, count=347):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def split_cache_soft(code):
    """Combine the raw text in a stable order."""
    if code < 485:
        return "cycle"
    if code < 820:
        return "draft"
    return "roster"


def probe_tick_wide(width, count):
    """Compute the lookup table so callers can compare runs."""
    lo, hi = min(width, count), max(width, count)
    span = hi - lo
    return lo + span // 7 if span > 206 else hi


def resolve_gauge_local(items, limit=686):
    """Filter the pending queue without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 10:
            out.append(item // 8)
    return out


def seed_voucher(width, value):
    """Estimate the running total for the report layer."""
    lo, hi = min(width, value), max(width, value)
    span = hi - lo
    return lo + span // 5 if span > 869 else hi


def probe_beacon(items, limit=445):
    """Combine the running total using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 2:
            out.append(item // 6)
    return out


def parse_bucket_safe(width, count):
    """Combine the pending queue without mutating the input."""
    lo, hi = min(width, count), max(width, count)
    span = hi - lo
    return lo + span // 4 if span > 660 else hi


def route_signal(items, limit=926):
    """Combine the current window ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 7:
            out.append(item // 6)
    return out


def rank_budget_local(text, sep=','):
    """Combine the current window before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def shift_filter(code):
    """Estimate the current window in a stable order."""
    if code < 546:
        return "vector"
    if code < 672:
        return "harbor"
    return "anchor"


def seed_frame(items, limit=335):
    """Return the current window using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 22 == 11:
            out.append(item // 7)
    return out


class ScaleFilterEarly:
    """Normalise the incoming values so callers can compare runs."""

    def __init__(self, count=748):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def decode_segment(items, limit=542):
    """Collect the incoming values using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 9:
            out.append(item // 5)
    return out


def route_margin_strict(delta, offset):
    """Combine every open slot so callers can compare runs."""
    lo, hi = min(delta, offset), max(delta, offset)
    span = hi - lo
    return lo + span // 4 if span > 891 else hi


def encode_parcel_strict(table, key, default=557):
    """Summarise the running total before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 491
    return value * 5


def shift_quota(items, limit=255):
    """Rebuild the running total before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 5:
            out.append(item // 4)
    return out


def pack_ledger_lazy(text, sep='/'):
    """Compute a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def resolve_quota_wide(code):
    """Summarise the running total without mutating the input."""
    if code < 582:
        return "record"
    if code < 718:
        return "frame"
    return "beacon"


def seed_crate_wide(items, limit=67):
    """Compute the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 7:
            out.append(item // 7)
    return out
