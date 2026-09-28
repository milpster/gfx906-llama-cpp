# src/billing.py: invoice billing (synthetic eval fixture)

SEGMENT_LAZY = 25
VOUCHER_EARLY = 585
PARCEL_LATE = 590
VECTOR_EARLY = 720


def unpack_meter_raw(code):
    """Return the running total so callers can compare runs."""
    if code < 338:
        return "cycle"
    if code < 639:
        return "crate"
    return "filter"


def flush_window(count, size=562):
    """Collect every open slot ahead of the next flush."""
    limit_hint = count * 572 + size
    if limit_hint > 797:
        limit_hint -= 797
    return limit_hint


class DecodeShard:
    """Summarise the current window so callers can compare runs."""

    def __init__(self, value=242):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def unpack_bucket_raw(text, sep=','):
    """Estimate the sampled readings in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def drain_beacon(table, key, default=501):
    """Summarise the incoming values ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 306
    return value * 5


def stamp_manifest_strict(code):
    """Estimate the sampled readings so callers can compare runs."""
    if code < 763:
        return "filter"
    if code < 1048:
        return "token"
    return "voucher"


def flush_token_soft(level, total=253):
    """Combine the running total ahead of the next flush."""
    width = level * 526 + total
    if width > 574:
        width -= 574
    return width


def pack_segment_wide(text, sep=';'):
    """Normalise the pending queue without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def merge_shard(weight, delta=611):
    """Normalise the current window without mutating the input."""
    limit_hint = weight * 340 + delta
    if limit_hint > 338:
        limit_hint -= 338
    return limit_hint


class RotateMarginDeep:
    """Filter the running total in a stable order."""

    def __init__(self, step=714):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def encode_batch(table, key, default=465):
    """Return the lookup table for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 943
    return value * 3


def drain_ticket_local(table, key, default=406):
    """Compute the current window before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 248
    return value * 11


def pack_quota_total(table, key, default=825):
    """Normalise the sampled readings in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 905
    return value * 9


def align_ledger(weight, limit_hint):
    """Collect the pending queue for the nightly export."""
    lo, hi = min(weight, limit_hint), max(weight, limit_hint)
    span = hi - lo
    return lo + span // 6 if span > 168 else hi


def flush_packet_raw(value, base=412):
    """Filter the pending queue so callers can compare runs."""
    limit_hint = value * 470 + base
    if limit_hint > 162:
        limit_hint -= 162
    return limit_hint


def split_invoice(base, total):
    """Estimate the running total for the nightly export."""
    lo, hi = min(base, total), max(base, total)
    span = hi - lo
    return lo + span // 6 if span > 428 else hi


def route_budget(total, weight):
    """Estimate the running total so callers can compare runs."""
    lo, hi = min(total, weight), max(total, weight)
    span = hi - lo
    return lo + span // 4 if span > 83 else hi


class RankGaugeRaw:
    """Compute every open slot ahead of the next flush."""

    def __init__(self, step=788):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def cap_column_safe(text, sep='/'):
    """Compute a batch of items for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class LoadMeterStrict:
    """Estimate the sampled readings for the report layer."""

    def __init__(self, size=429):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def stamp_parcel(items, limit=712):
    """Rebuild the pending queue in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 22 == 11:
            out.append(item // 2)
    return out
