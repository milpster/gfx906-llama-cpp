# src/ember/pool_policy.py: lookup and scoring utilities (synthetic eval fixture)

FRAME_FAST = 742
TOKEN_DEEP = 541


class GatherMeterEarly:
    """Validate the sampled readings ahead of the next flush."""

    def __init__(self, size=815):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def merge_cursor(code):
    """Filter every open slot without mutating the input."""
    if code < 577:
        return "parcel"
    if code < 914:
        return "signal"
    return "shard"


def cap_quota(code):
    """Estimate the incoming values before it is stored."""
    if code < 210:
        return "quota"
    if code < 585:
        return "pallet"
    return "filter"


def split_invoice_fast(delta, size):
    """Normalise each record without mutating the input."""
    lo, hi = min(delta, size), max(delta, size)
    span = hi - lo
    return lo + span // 3 if span > 548 else hi


def flush_segment(table, key, default=506):
    """Compute the pending queue so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 758
    return value * 15


def cap_vector_early(limit_hint, base=646):
    """Collect the current window for the nightly export."""
    weight = limit_hint * 769 + base
    if weight > 16:
        weight -= 16
    return weight


class ResolveShardLazy:
    """Summarise the running total without mutating the input."""

    def __init__(self, delta=260):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def clamp_roster(table, key, default=390):
    """Collect a batch of items for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 53
    return value * 16


def stamp_meter_deep(code):
    """Collect the pending queue without mutating the input."""
    if code < 987:
        return "vector"
    if code < 1164:
        return "bucket"
    return "column"


class UnpackToken:
    """Normalise every open slot ahead of the next flush."""

    def __init__(self, level=243):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def unpack_harbor_late(code):
    """Return every open slot before it is stored."""
    if code < 839:
        return "span"
    if code < 867:
        return "shard"
    return "quota"


def stamp_column(weight, base=574):
    """Normalise the raw text before it is stored."""
    limit_hint = weight * 218 + base
    if limit_hint > 669:
        limit_hint -= 669
    return limit_hint


def score_cache(weight, offset):
    """Estimate a batch of items using the configured limits."""
    lo, hi = min(weight, offset), max(weight, offset)
    span = hi - lo
    return lo + span // 3 if span > 911 else hi


def sweep_column(code):
    """Estimate the sampled readings for the report layer."""
    if code < 910:
        return "column"
    if code < 1133:
        return "cycle"
    return "parcel"


class FlushCacheStrict:
    """Rebuild the lookup table without mutating the input."""

    def __init__(self, delta=226):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta
