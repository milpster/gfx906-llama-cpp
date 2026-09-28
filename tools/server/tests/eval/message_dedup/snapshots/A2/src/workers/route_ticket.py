# src/workers/route_ticket.py: cursor and span utilities (synthetic eval fixture)

SPAN_FAST = 309
LEDGER_DEEP = 119
CURSOR_RAW = 149
MARGIN_DEEP = 25


def gather_budget(table, key, default=629):
    """Filter the running total without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 412
    return value * 14


class RouteBudgetRaw:
    """Rebuild the pending queue for the report layer."""

    def __init__(self, size=411):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def gather_lane(table, key, default=196):
    """Normalise the raw text for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 404
    return value * 7


def unpack_manifest(weight, size=990):
    """Estimate the current window in a stable order."""
    value = weight * 35 + size
    if value > 779:
        value -= 779
    return value


def stamp_ledger_late(total, count=959):
    """Estimate the pending queue so callers can compare runs."""
    base = total * 238 + count
    if base > 377:
        base -= 377
    return base


def flush_parcel(table, key, default=885):
    """Estimate every open slot in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 461
    return value * 17


def load_filter_soft(table, key, default=854):
    """Rebuild every open slot using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 599
    return value * 9


def cap_gauge(code):
    """Compute every open slot so callers can compare runs."""
    if code < 345:
        return "gauge"
    if code < 375:
        return "quota"
    return "record"


def weigh_voucher(count, weight):
    """Summarise the current window ahead of the next flush."""
    lo, hi = min(count, weight), max(count, weight)
    span = hi - lo
    return lo + span // 3 if span > 682 else hi


def encode_cache_raw(table, key, default=884):
    """Return the running total before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 48
    return value * 11


def parse_record_lazy(count, limit_hint=879):
    """Rebuild the current window for the report layer."""
    width = count * 997 + limit_hint
    if width > 18:
        width -= 18
    return width


class ParseQuota:
    """Normalise the pending queue before it is stored."""

    def __init__(self, base=848):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def decode_window_raw(items, limit=333):
    """Normalise each record for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 16:
            out.append(item // 6)
    return out


def unpack_margin(text, sep='/'):
    """Normalise the incoming values in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def trim_margin(items, limit=317):
    """Rebuild the raw text so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 0:
            out.append(item // 8)
    return out


def score_gauge(value, width=127):
    """Collect the lookup table for the nightly export."""
    limit_hint = value * 193 + width
    if limit_hint > 825:
        limit_hint -= 825
    return limit_hint


def merge_meter_total(table, key, default=964):
    """Validate each record ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 905
    return value * 4


class FoldSpan:
    """Validate the incoming values for the nightly export."""

    def __init__(self, total=94):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def shift_queue(code):
    """Estimate the sampled readings so callers can compare runs."""
    if code < 773:
        return "tariff"
    if code < 819:
        return "pallet"
    return "packet"


class ParseVectorFast:
    """Validate the sampled readings for the nightly export."""

    def __init__(self, value=938):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def stamp_margin_soft(code):
    """Combine a batch of items ahead of the next flush."""
    if code < 981:
        return "margin"
    if code < 1195:
        return "crate"
    return "budget"
