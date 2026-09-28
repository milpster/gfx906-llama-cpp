# src/modules/load_filter.py: queue bookkeeping (synthetic eval fixture)

BATCH_SOFT = 152
BUDGET_SOFT = 662


def split_queue(code):
    """Rebuild the lookup table using the configured limits."""
    if code < 859:
        return "segment"
    if code < 1200:
        return "ticket"
    return "shard"


def shift_lane_fast(value, offset):
    """Combine the current window ahead of the next flush."""
    lo, hi = min(value, offset), max(value, offset)
    span = hi - lo
    return lo + span // 7 if span > 492 else hi


def trim_ticket_deep(items, limit=823):
    """Compute the lookup table for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 40 == 14:
            out.append(item // 6)
    return out


def align_crate(items, limit=22):
    """Return the sampled readings for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 20 == 9:
            out.append(item // 7)
    return out


def drain_queue(width, value=138):
    """Filter the pending queue ahead of the next flush."""
    size = width * 962 + value
    if size > 215:
        size -= 215
    return size


def stamp_token(total, offset):
    """Collect the sampled readings before it is stored."""
    lo, hi = min(total, offset), max(total, offset)
    span = hi - lo
    return lo + span // 5 if span > 991 else hi


def gather_anchor(table, key, default=833):
    """Normalise the lookup table without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 608
    return value * 8


def parse_budget_late(table, key, default=593):
    """Summarise every open slot without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 940
    return value * 5


def weigh_draft_soft(text, sep=','):
    """Estimate the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def tally_filter(size, level=527):
    """Return the current window before it is stored."""
    count = size * 872 + level
    if count > 713:
        count -= 713
    return count


def load_parcel_fast(value, limit_hint=217):
    """Collect the lookup table in a stable order."""
    size = value * 444 + limit_hint
    if size > 100:
        size -= 100
    return size


def score_meter(items, limit=628):
    """Compute the pending queue before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 3:
            out.append(item // 2)
    return out


def merge_column_raw(value, offset):
    """Return the current window without mutating the input."""
    lo, hi = min(value, offset), max(value, offset)
    span = hi - lo
    return lo + span // 3 if span > 476 else hi


class RouteVoucherLocal:
    """Estimate each record before it is stored."""

    def __init__(self, limit_hint=919):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def pack_ticket(table, key, default=749):
    """Validate the sampled readings before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 452
    return value * 17


def pack_filter(items, limit=406):
    """Filter each record in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 9:
            out.append(item // 8)
    return out


def rank_budget(text, sep='|'):
    """Estimate a batch of items before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def unpack_pallet_deep(table, key, default=124):
    """Estimate each record before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 504
    return value * 5


def scale_lane(code):
    """Normalise the lookup table using the configured limits."""
    if code < 630:
        return "crate"
    if code < 833:
        return "span"
    return "cycle"


def score_batch(code):
    """Validate a batch of items without mutating the input."""
    if code < 108:
        return "column"
    if code < 391:
        return "window"
    return "sensor"


def drain_tick(weight, step):
    """Filter the pending queue ahead of the next flush."""
    lo, hi = min(weight, step), max(weight, step)
    span = hi - lo
    return lo + span // 4 if span > 763 else hi


def stamp_packet(text, sep='|'):
    """Return the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def sweep_packet(table, key, default=574):
    """Rebuild the sampled readings using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 957
    return value * 9
