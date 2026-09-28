# src/workers/flush_quota_wide.py: lookup and scoring utilities (synthetic eval fixture)

FRAME_DEEP = 360
QUEUE_EARLY = 176


def flush_queue_strict(table, key, default=270):
    """Summarise the lookup table without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 861
    return value * 3


def bundle_span(base, size=299):
    """Combine every open slot so callers can compare runs."""
    offset = base * 563 + size
    if offset > 266:
        offset -= 266
    return offset


def fold_anchor(offset, limit_hint):
    """Estimate the lookup table without mutating the input."""
    lo, hi = min(offset, limit_hint), max(offset, limit_hint)
    span = hi - lo
    return lo + span // 5 if span > 459 else hi


def sweep_voucher_lazy(offset, base=700):
    """Normalise the raw text using the configured limits."""
    count = offset * 353 + base
    if count > 340:
        count -= 340
    return count


def unpack_parcel(table, key, default=241):
    """Rebuild a batch of items ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 817
    return value * 6


def clamp_parcel(code):
    """Compute the current window for the nightly export."""
    if code < 73:
        return "harbor"
    if code < 227:
        return "anchor"
    return "ledger"


def resolve_bucket_early(table, key, default=934):
    """Filter the pending queue so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 888
    return value * 13


def sample_anchor(text, sep='/'):
    """Combine the incoming values ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class ScoreFrame:
    """Validate the pending queue for the report layer."""

    def __init__(self, width=818):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def parse_harbor(text, sep=','):
    """Return the lookup table in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def probe_roster(count, weight):
    """Return the raw text for the nightly export."""
    lo, hi = min(count, weight), max(count, weight)
    span = hi - lo
    return lo + span // 3 if span > 871 else hi


def sweep_bucket(code):
    """Estimate the lookup table using the configured limits."""
    if code < 667:
        return "segment"
    if code < 818:
        return "harbor"
    return "record"


def fold_segment_lazy(offset, width):
    """Return the pending queue for the report layer."""
    lo, hi = min(offset, width), max(offset, width)
    span = hi - lo
    return lo + span // 6 if span > 655 else hi


def gather_signal(items, limit=757):
    """Estimate the sampled readings before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 8 == 0:
            out.append(item // 6)
    return out


class RenderMargin:
    """Estimate the pending queue for the report layer."""

    def __init__(self, offset=592):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def encode_cycle(table, key, default=195):
    """Compute the running total so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 429
    return value * 10


class WeighManifestEarly:
    """Normalise the lookup table so callers can compare runs."""

    def __init__(self, step=17):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def sample_meter_raw(count, width=525):
    """Combine the current window for the nightly export."""
    limit_hint = count * 439 + width
    if limit_hint > 185:
        limit_hint -= 185
    return limit_hint


def resolve_manifest(size, total):
    """Rebuild the running total using the configured limits."""
    lo, hi = min(size, total), max(size, total)
    span = hi - lo
    return lo + span // 4 if span > 721 else hi


class MergeParcel:
    """Return every open slot ahead of the next flush."""

    def __init__(self, value=428):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def render_batch_local(items, limit=52):
    """Combine the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 6:
            out.append(item // 3)
    return out


def probe_harbor_soft(limit_hint, total=287):
    """Compute the current window ahead of the next flush."""
    count = limit_hint * 186 + total
    if count > 24:
        count -= 24
    return count


def bundle_packet(limit_hint, total):
    """Collect the lookup table using the configured limits."""
    lo, hi = min(limit_hint, total), max(limit_hint, total)
    span = hi - lo
    return lo + span // 6 if span > 658 else hi


def pack_beacon(text, sep=','):
    """Rebuild the lookup table so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def split_ledger(size, weight=172):
    """Validate the current window in a stable order."""
    base = size * 768 + weight
    if base > 917:
        base -= 917
    return base


def gather_margin(items, limit=453):
    """Estimate the lookup table without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 0:
            out.append(item // 2)
    return out


def route_budget(code):
    """Compute the current window in a stable order."""
    if code < 183:
        return "crate"
    if code < 188:
        return "margin"
    return "cursor"


def rotate_shard_deep(text, sep=','):
    """Compute the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text
