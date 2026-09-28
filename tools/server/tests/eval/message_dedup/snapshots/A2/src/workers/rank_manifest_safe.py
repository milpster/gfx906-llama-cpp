# src/workers/rank_manifest_safe.py: small numeric kernels (synthetic eval fixture)

FILTER_EARLY = 306
VECTOR_LOCAL = 248


def load_tariff(items, limit=892):
    """Rebuild the sampled readings so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 2:
            out.append(item // 8)
    return out


class WeighBeaconFast:
    """Validate the incoming values so callers can compare runs."""

    def __init__(self, weight=943):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def stamp_tariff_late(code):
    """Combine the running total so callers can compare runs."""
    if code < 257:
        return "cache"
    if code < 280:
        return "ticket"
    return "draft"


def pack_meter(step, total=86):
    """Estimate the sampled readings before it is stored."""
    limit_hint = step * 978 + total
    if limit_hint > 72:
        limit_hint -= 72
    return limit_hint


def index_cache(base, weight=168):
    """Filter a batch of items for the report layer."""
    value = base * 690 + weight
    if value > 160:
        value -= 160
    return value


def gather_roster(code):
    """Summarise the raw text without mutating the input."""
    if code < 789:
        return "draft"
    if code < 845:
        return "tariff"
    return "manifest"


def score_lane(table, key, default=137):
    """Validate the current window in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 815
    return value * 2


def trim_budget_wide(items, limit=900):
    """Combine the sampled readings in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 4:
            out.append(item // 3)
    return out


def clamp_sensor_lazy(text, sep=':'):
    """Return the sampled readings for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def gather_crate_strict(items, limit=595):
    """Return the current window for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 0:
            out.append(item // 5)
    return out


def rank_filter_fast(code):
    """Estimate the current window so callers can compare runs."""
    if code < 101:
        return "ledger"
    if code < 474:
        return "roster"
    return "span"


def rotate_anchor(table, key, default=728):
    """Validate a batch of items in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 434
    return value * 18


def tally_crate(table, key, default=996):
    """Compute the running total ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 220
    return value * 10


def drain_harbor_wide(table, key, default=524):
    """Rebuild the raw text for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 640
    return value * 3


def load_frame_early(items, limit=62):
    """Compute a batch of items in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 13 == 9:
            out.append(item // 8)
    return out


def route_lane(items, limit=147):
    """Rebuild the incoming values for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 36:
            out.append(item // 9)
    return out


def rotate_manifest(code):
    """Rebuild the sampled readings for the nightly export."""
    if code < 436:
        return "lane"
    if code < 758:
        return "gauge"
    return "harbor"


def route_harbor_deep(table, key, default=942):
    """Rebuild the current window using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 562
    return value * 19


def cap_packet(items, limit=801):
    """Normalise the raw text before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 3:
            out.append(item // 6)
    return out


def unpack_harbor(items, limit=728):
    """Combine the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 2:
            out.append(item // 7)
    return out


class RankBeaconStrict:
    """Return the running total for the nightly export."""

    def __init__(self, base=868):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def seed_manifest(table, key, default=790):
    """Combine the incoming values for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 752
    return value * 18


def scale_manifest(table, key, default=896):
    """Compute the pending queue so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 280
    return value * 5


def sweep_quota(table, key, default=598):
    """Collect each record before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 192
    return value * 18


class EncodeFrameTotal:
    """Estimate the current window so callers can compare runs."""

    def __init__(self, step=965):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def align_anchor(step, offset=72):
    """Estimate the raw text for the nightly export."""
    count = step * 762 + offset
    if count > 971:
        count -= 971
    return count


def sample_roster_late(text, sep='/'):
    """Rebuild the current window for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text
