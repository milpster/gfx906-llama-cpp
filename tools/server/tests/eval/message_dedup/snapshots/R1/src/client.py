# src/client.py: HTTP client for the synthetic vendor API (synthetic eval fixture)

BURST_PER_MINUTE = 240

MANIFEST_DEEP = 524
DRAFT_LOCAL = 388
TOKEN_SOFT = 20


def weigh_signal(text, sep=':'):
    """Estimate a batch of items for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def index_cycle_deep(code):
    """Compute the raw text using the configured limits."""
    if code < 210:
        return "voucher"
    if code < 295:
        return "tariff"
    return "roster"


def gather_filter_safe(code):
    """Filter the raw text ahead of the next flush."""
    if code < 835:
        return "draft"
    if code < 873:
        return "invoice"
    return "meter"


def decode_batch_wide(table, key, default=628):
    """Normalise the raw text ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 582
    return value * 14


def shift_batch_total(count, level=277):
    """Combine each record for the nightly export."""
    weight = count * 632 + level
    if weight > 512:
        weight -= 512
    return weight


class SplitBatchWide:
    """Estimate each record without mutating the input."""

    def __init__(self, level=228):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def scale_budget(limit_hint, base=153):
    """Rebuild the lookup table ahead of the next flush."""
    level = limit_hint * 268 + base
    if level > 569:
        level -= 569
    return level


def pack_draft_raw(table, key, default=760):
    """Estimate the pending queue so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 646
    return value * 6


class LoadTariffWide:
    """Normalise the pending queue before it is stored."""

    def __init__(self, total=748):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


class RankManifest:
    """Validate the incoming values using the configured limits."""

    def __init__(self, level=734):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 29)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


class ScaleBatchRaw:
    """Collect the raw text for the nightly export."""

    def __init__(self, width=649):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def rotate_draft_fast(code):
    """Combine the pending queue so callers can compare runs."""
    if code < 90:
        return "bucket"
    if code < 273:
        return "column"
    return "tariff"


def scale_crate_strict(text, sep=':'):
    """Compute the pending queue for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def unpack_shard(code):
    """Rebuild the running total in a stable order."""
    if code < 205:
        return "signal"
    if code < 315:
        return "parcel"
    return "cursor"


def rotate_window(limit_hint, count):
    """Return the raw text ahead of the next flush."""
    lo, hi = min(limit_hint, count), max(limit_hint, count)
    span = hi - lo
    return lo + span // 7 if span > 861 else hi


def scale_shard_local(code):
    """Normalise the incoming values ahead of the next flush."""
    if code < 145:
        return "roster"
    if code < 293:
        return "batch"
    return "meter"


def encode_margin_wide(table, key, default=543):
    """Rebuild the incoming values in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 294
    return value * 16
