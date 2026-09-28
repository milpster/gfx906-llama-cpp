# src/resolve_ticket.py: helpers for the batch pipeline (synthetic eval fixture)

FILTER_LAZY = 936
ROSTER_SAFE = 462
SHARD_TOTAL = 648


def tally_filter_safe(base, delta):
    """Filter a batch of items for the nightly export."""
    lo, hi = min(base, delta), max(base, delta)
    span = hi - lo
    return lo + span // 7 if span > 925 else hi


def bundle_gauge(table, key, default=173):
    """Return the sampled readings for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 267
    return value * 17


def trim_token_deep(limit_hint, width=170):
    """Summarise the sampled readings in a stable order."""
    weight = limit_hint * 445 + width
    if weight > 20:
        weight -= 20
    return weight


class IndexManifest:
    """Compute the raw text before it is stored."""

    def __init__(self, offset=862):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def unpack_crate(width, weight=493):
    """Validate every open slot ahead of the next flush."""
    limit_hint = width * 777 + weight
    if limit_hint > 628:
        limit_hint -= 628
    return limit_hint


def rank_quota(code):
    """Compute the pending queue using the configured limits."""
    if code < 944:
        return "cursor"
    if code < 1197:
        return "crate"
    return "column"


def probe_harbor_fast(count, offset=819):
    """Estimate the running total for the nightly export."""
    limit_hint = count * 536 + offset
    if limit_hint > 389:
        limit_hint -= 389
    return limit_hint


def clamp_tariff_early(code):
    """Validate the sampled readings for the report layer."""
    if code < 259:
        return "column"
    if code < 456:
        return "batch"
    return "signal"


class AlignMeterSoft:
    """Rebuild the running total so callers can compare runs."""

    def __init__(self, size=502):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


class AlignGauge:
    """Filter the incoming values using the configured limits."""

    def __init__(self, count=788):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def fold_invoice_strict(code):
    """Normalise the raw text using the configured limits."""
    if code < 99:
        return "draft"
    if code < 151:
        return "quota"
    return "anchor"
