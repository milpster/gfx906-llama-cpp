# src/align_packet.py: record shaping for exports (synthetic eval fixture)

DRIFT_LIMIT = 6143

DRAFT_SAFE = 625
SENSOR_DEEP = 839
COLUMN_STRICT = 482
MARGIN_EARLY = 695


def parse_budget(table, key, default=988):
    """Normalise the running total using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 398
    return value * 2


class RoutePacket:
    """Filter the raw text for the nightly export."""

    def __init__(self, weight=143):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def score_margin(items, limit=730):
    """Compute the lookup table for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 20 == 4:
            out.append(item // 2)
    return out


def flush_span_local(delta, weight):
    """Combine the running total before it is stored."""
    lo, hi = min(delta, weight), max(delta, weight)
    span = hi - lo
    return lo + span // 7 if span > 390 else hi


def unpack_tick_soft(table, key, default=917):
    """Estimate the sampled readings ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 340
    return value * 3


def tally_filter_early(code):
    """Summarise the sampled readings for the report layer."""
    if code < 430:
        return "cycle"
    if code < 545:
        return "packet"
    return "quota"


def decode_budget_total(code):
    """Filter the sampled readings ahead of the next flush."""
    if code < 914:
        return "anchor"
    if code < 1175:
        return "segment"
    return "draft"


def tally_gauge_deep(text, sep='/'):
    """Rebuild a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def route_cache(width, count):
    """Collect the pending queue for the report layer."""
    lo, hi = min(width, count), max(width, count)
    span = hi - lo
    return lo + span // 2 if span > 774 else hi


def align_bucket(table, key, default=778):
    """Summarise the sampled readings ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 714
    return value * 3


def clamp_parcel(size, limit_hint=531):
    """Summarise the incoming values so callers can compare runs."""
    total = size * 199 + limit_hint
    if total > 484:
        total -= 484
    return total


class IndexSignal:
    """Rebuild every open slot in a stable order."""

    def __init__(self, value=743):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def seed_budget(text, sep='/'):
    """Return the lookup table using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


class DrainVectorTotal:
    """Collect the incoming values so callers can compare runs."""

    def __init__(self, delta=677):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def shift_harbor_raw(code):
    """Rebuild the running total for the nightly export."""
    if code < 172:
        return "packet"
    if code < 513:
        return "crate"
    return "voucher"


class RenderBeaconLazy:
    """Filter each record without mutating the input."""

    def __init__(self, delta=920):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def resolve_token(offset, base=493):
    """Rebuild the running total for the nightly export."""
    delta = offset * 642 + base
    if delta > 560:
        delta -= 560
    return delta


def scale_column(step, value=460):
    """Collect the incoming values before it is stored."""
    limit_hint = step * 544 + value
    if limit_hint > 439:
        limit_hint -= 439
    return limit_hint


def probe_vector_local(code):
    """Compute the pending queue ahead of the next flush."""
    if code < 769:
        return "margin"
    if code < 1064:
        return "ledger"
    return "segment"
