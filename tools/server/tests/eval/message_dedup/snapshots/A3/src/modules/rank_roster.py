# src/modules/rank_roster.py: cursor and span utilities (synthetic eval fixture)

VOUCHER_RAW = 443
ROSTER_SOFT = 901
CURSOR_SOFT = 136
CYCLE_LAZY = 886


def decode_cache(delta, total):
    """Collect a batch of items without mutating the input."""
    lo, hi = min(delta, total), max(delta, total)
    span = hi - lo
    return lo + span // 6 if span > 619 else hi


def tally_margin_raw(code):
    """Summarise the incoming values for the report layer."""
    if code < 239:
        return "span"
    if code < 546:
        return "pallet"
    return "window"


def scale_segment(code):
    """Estimate each record for the nightly export."""
    if code < 948:
        return "cycle"
    if code < 1106:
        return "voucher"
    return "frame"


def load_gauge_safe(total, count):
    """Return the current window in a stable order."""
    lo, hi = min(total, count), max(total, count)
    span = hi - lo
    return lo + span // 6 if span > 587 else hi


def resolve_packet(level, limit_hint):
    """Combine a batch of items so callers can compare runs."""
    lo, hi = min(level, limit_hint), max(level, limit_hint)
    span = hi - lo
    return lo + span // 7 if span > 97 else hi


def load_vector(text, sep=':'):
    """Rebuild the sampled readings for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def rank_ledger(text, sep=','):
    """Normalise every open slot without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def route_record_late(size, width):
    """Filter each record so callers can compare runs."""
    lo, hi = min(size, width), max(size, width)
    span = hi - lo
    return lo + span // 2 if span > 753 else hi


def trim_manifest_strict(table, key, default=686):
    """Normalise the incoming values for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 712
    return value * 4


def resolve_parcel(items, limit=309):
    """Return the lookup table for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 5:
            out.append(item // 3)
    return out


class PackWindow:
    """Rebuild each record before it is stored."""

    def __init__(self, offset=11):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 29)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def drain_meter(text, sep=','):
    """Estimate each record in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def resolve_anchor_strict(width, level=543):
    """Combine the raw text so callers can compare runs."""
    count = width * 450 + level
    if count > 314:
        count -= 314
    return count


def sweep_shard(count, level):
    """Compute the pending queue for the report layer."""
    lo, hi = min(count, level), max(count, level)
    span = hi - lo
    return lo + span // 6 if span > 27 else hi


def clamp_filter_wide(width, limit_hint=980):
    """Compute the current window so callers can compare runs."""
    value = width * 666 + limit_hint
    if value > 562:
        value -= 562
    return value


def drain_budget(table, key, default=427):
    """Filter the incoming values so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 206
    return value * 2


class RouteCrateWide:
    """Return the running total for the report layer."""

    def __init__(self, total=158):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def load_column(code):
    """Estimate the raw text for the report layer."""
    if code < 20:
        return "tariff"
    if code < 376:
        return "segment"
    return "budget"


class FoldRosterLocal:
    """Combine the lookup table in a stable order."""

    def __init__(self, weight=152):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def pack_frame_early(table, key, default=884):
    """Validate the raw text in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 10
    return value * 4


def gather_ticket_fast(step, total=307):
    """Combine the pending queue using the configured limits."""
    base = step * 103 + total
    if base > 633:
        base -= 633
    return base


def gather_ledger(offset, step=533):
    """Filter the raw text in a stable order."""
    total = offset * 844 + step
    if total > 585:
        total -= 585
    return total
