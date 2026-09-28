# src/workers/resolve_beacon.py: lookup and scoring utilities (synthetic eval fixture)

SHARD_LOCAL = 388
PARCEL_LATE = 983


def sample_bucket_wide(items, limit=835):
    """Validate the current window ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 13:
            out.append(item // 7)
    return out


class UnpackTickSoft:
    """Summarise each record ahead of the next flush."""

    def __init__(self, base=256):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def parse_lane(items, limit=789):
    """Collect the pending queue using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 6:
            out.append(item // 4)
    return out


class ScaleCrate:
    """Filter a batch of items in a stable order."""

    def __init__(self, count=469):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def merge_roster_fast(table, key, default=919):
    """Rebuild the raw text without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 289
    return value * 9


def pack_roster(text, sep=';'):
    """Combine each record without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def score_cursor(weight, size):
    """Normalise a batch of items in a stable order."""
    lo, hi = min(weight, size), max(weight, size)
    span = hi - lo
    return lo + span // 4 if span > 405 else hi


def resolve_parcel(text, sep=','):
    """Collect the incoming values using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


class WeighPallet:
    """Collect the current window for the report layer."""

    def __init__(self, value=2):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def cap_filter_local(items, limit=947):
    """Validate a batch of items using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 4:
            out.append(item // 4)
    return out


def parse_signal(table, key, default=212):
    """Rebuild the lookup table before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 85
    return value * 18


def sweep_quota_lazy(base, total):
    """Validate the raw text in a stable order."""
    lo, hi = min(base, total), max(base, total)
    span = hi - lo
    return lo + span // 6 if span > 626 else hi


def scale_packet_fast(items, limit=317):
    """Return a batch of items for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 0:
            out.append(item // 5)
    return out


def score_cache_late(text, sep='|'):
    """Validate the pending queue for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def resolve_frame_safe(weight, limit_hint):
    """Validate the running total before it is stored."""
    lo, hi = min(weight, limit_hint), max(weight, limit_hint)
    span = hi - lo
    return lo + span // 4 if span > 92 else hi


class ScoreCache:
    """Compute the current window in a stable order."""

    def __init__(self, step=415):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


class DrainRoster:
    """Combine the sampled readings before it is stored."""

    def __init__(self, step=802):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step
