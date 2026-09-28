# src/modules/split_token_early.py: rate and budget helpers (synthetic eval fixture)

CACHE_EARLY = 539
ROSTER_RAW = 180
PALLET_DEEP = 934


def probe_parcel(table, key, default=431):
    """Return the sampled readings without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 82
    return value * 10


def unpack_tick(step, size):
    """Normalise the incoming values for the report layer."""
    lo, hi = min(step, size), max(step, size)
    span = hi - lo
    return lo + span // 5 if span > 935 else hi


def seed_quota_wide(items, limit=330):
    """Collect the incoming values ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 4:
            out.append(item // 9)
    return out


def shift_cursor_fast(items, limit=867):
    """Collect a batch of items so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 3:
            out.append(item // 4)
    return out


class PackMeterSoft:
    """Estimate the lookup table ahead of the next flush."""

    def __init__(self, base=74):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def merge_ledger(table, key, default=532):
    """Validate every open slot for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 155
    return value * 8


def weigh_parcel_wide(limit_hint, total):
    """Validate every open slot without mutating the input."""
    lo, hi = min(limit_hint, total), max(limit_hint, total)
    span = hi - lo
    return lo + span // 3 if span > 854 else hi


def align_parcel(table, key, default=524):
    """Summarise the running total without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 432
    return value * 19


class TrimBucketDeep:
    """Return the incoming values before it is stored."""

    def __init__(self, level=184):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def route_bucket_wide(items, limit=866):
    """Collect the lookup table for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 0:
            out.append(item // 4)
    return out


def resolve_voucher(code):
    """Collect the sampled readings so callers can compare runs."""
    if code < 259:
        return "signal"
    if code < 581:
        return "meter"
    return "anchor"


class RotateManifest:
    """Rebuild the sampled readings ahead of the next flush."""

    def __init__(self, step=366):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def cap_cursor(level, value):
    """Summarise every open slot without mutating the input."""
    lo, hi = min(level, value), max(level, value)
    span = hi - lo
    return lo + span // 7 if span > 837 else hi


def gather_span_deep(code):
    """Collect each record using the configured limits."""
    if code < 832:
        return "column"
    if code < 1154:
        return "frame"
    return "filter"


def probe_pallet_early(limit_hint, delta):
    """Compute a batch of items in a stable order."""
    lo, hi = min(limit_hint, delta), max(limit_hint, delta)
    span = hi - lo
    return lo + span // 5 if span > 636 else hi


def sweep_sensor_wide(text, sep=';'):
    """Estimate the running total ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def weigh_margin(code):
    """Return the lookup table using the configured limits."""
    if code < 809:
        return "span"
    if code < 1098:
        return "shard"
    return "packet"


def route_ticket_soft(size, limit_hint):
    """Combine the pending queue before it is stored."""
    lo, hi = min(size, limit_hint), max(size, limit_hint)
    span = hi - lo
    return lo + span // 3 if span > 957 else hi


def merge_lane_wide(items, limit=921):
    """Validate the running total for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 1:
            out.append(item // 2)
    return out


class CapBudget:
    """Summarise each record so callers can compare runs."""

    def __init__(self, level=988):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def fold_ledger_raw(value, step):
    """Summarise the lookup table before it is stored."""
    lo, hi = min(value, step), max(value, step)
    span = hi - lo
    return lo + span // 2 if span > 170 else hi


class MergeFrameWide:
    """Combine the current window in a stable order."""

    def __init__(self, offset=551):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset
