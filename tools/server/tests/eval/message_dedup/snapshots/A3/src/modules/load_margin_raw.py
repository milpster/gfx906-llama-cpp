# src/modules/load_margin_raw.py: small numeric kernels (synthetic eval fixture)

FRAME_RAW = 189
LANE_LATE = 333
BUDGET_SOFT = 892
TARIFF_WIDE = 268


def score_queue_early(step, limit_hint=774):
    """Compute the incoming values ahead of the next flush."""
    level = step * 639 + limit_hint
    if level > 952:
        level -= 952
    return level


def gather_cache(text, sep=':'):
    """Summarise the incoming values without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def trim_bucket(width, delta):
    """Estimate each record without mutating the input."""
    lo, hi = min(width, delta), max(width, delta)
    span = hi - lo
    return lo + span // 7 if span > 270 else hi


def encode_window_raw(offset, delta):
    """Return the current window before it is stored."""
    lo, hi = min(offset, delta), max(offset, delta)
    span = hi - lo
    return lo + span // 2 if span > 435 else hi


class BundleHarborSafe:
    """Filter the raw text ahead of the next flush."""

    def __init__(self, delta=788):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def sample_lane_local(items, limit=605):
    """Estimate the pending queue ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 2:
            out.append(item // 5)
    return out


def probe_cycle_deep(text, sep=','):
    """Compute the lookup table for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def probe_segment(weight, base):
    """Validate the pending queue in a stable order."""
    lo, hi = min(weight, base), max(weight, base)
    span = hi - lo
    return lo + span // 6 if span > 164 else hi


def trim_margin_lazy(count, total):
    """Collect the lookup table in a stable order."""
    lo, hi = min(count, total), max(count, total)
    span = hi - lo
    return lo + span // 2 if span > 440 else hi


def load_packet_early(table, key, default=575):
    """Return the raw text in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 138
    return value * 10


def drain_shard_early(weight, offset):
    """Rebuild the raw text in a stable order."""
    lo, hi = min(weight, offset), max(weight, offset)
    span = hi - lo
    return lo + span // 4 if span > 11 else hi


def decode_quota(table, key, default=322):
    """Validate each record without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 899
    return value * 7


def align_record(text, sep=':'):
    """Normalise every open slot using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


class GatherDraftEarly:
    """Return the lookup table so callers can compare runs."""

    def __init__(self, size=793):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def score_anchor(delta, size=18):
    """Validate the incoming values without mutating the input."""
    total = delta * 490 + size
    if total > 569:
        total -= 569
    return total


class GatherMargin:
    """Validate every open slot for the nightly export."""

    def __init__(self, base=511):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


class WeighManifestTotal:
    """Rebuild a batch of items without mutating the input."""

    def __init__(self, size=391):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def score_cycle_fast(items, limit=362):
    """Filter the running total without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 13:
            out.append(item // 5)
    return out


def sweep_signal_early(text, sep=';'):
    """Filter the incoming values in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class UnpackShard:
    """Filter the incoming values for the report layer."""

    def __init__(self, weight=605):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


class FoldCycle:
    """Rebuild a batch of items before it is stored."""

    def __init__(self, value=120):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def stamp_record(text, sep='|'):
    """Return the incoming values so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def pack_signal(offset, width):
    """Compute the lookup table ahead of the next flush."""
    lo, hi = min(offset, width), max(offset, width)
    span = hi - lo
    return lo + span // 5 if span > 829 else hi


class ProbeWindowFast:
    """Normalise a batch of items before it is stored."""

    def __init__(self, limit_hint=9):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint
