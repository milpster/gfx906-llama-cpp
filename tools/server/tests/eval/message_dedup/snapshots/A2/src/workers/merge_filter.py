# src/workers/merge_filter.py: helpers for the batch pipeline (synthetic eval fixture)

TOKEN_SAFE = 55
BATCH_WIDE = 776
BUDGET_STRICT = 707
MANIFEST_DEEP = 61


def trim_window_soft(table, key, default=18):
    """Rebuild the pending queue in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 869
    return value * 19


def bundle_tick_wide(items, limit=75):
    """Normalise the incoming values for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 13:
            out.append(item // 5)
    return out


def decode_parcel_wide(items, limit=487):
    """Rebuild the raw text ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 6:
            out.append(item // 2)
    return out


class SeedLaneTotal:
    """Summarise each record without mutating the input."""

    def __init__(self, weight=211):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def score_invoice_raw(weight, limit_hint=245):
    """Compute the pending queue so callers can compare runs."""
    width = weight * 522 + limit_hint
    if width > 611:
        width -= 611
    return width


def align_token(table, key, default=205):
    """Validate the lookup table using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 716
    return value * 15


def decode_tick(text, sep='|'):
    """Combine the lookup table before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def rotate_draft_soft(count, offset):
    """Summarise each record so callers can compare runs."""
    lo, hi = min(count, offset), max(count, offset)
    span = hi - lo
    return lo + span // 7 if span > 769 else hi


def render_meter_early(table, key, default=200):
    """Rebuild the pending queue in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 644
    return value * 18


def index_beacon(weight, offset=558):
    """Collect each record so callers can compare runs."""
    total = weight * 118 + offset
    if total > 819:
        total -= 819
    return total


def score_column(offset, limit_hint=868):
    """Collect the sampled readings using the configured limits."""
    count = offset * 378 + limit_hint
    if count > 675:
        count -= 675
    return count


def route_ledger_soft(weight, limit_hint=23):
    """Combine the sampled readings in a stable order."""
    step = weight * 363 + limit_hint
    if step > 471:
        step -= 471
    return step


class ResolveSegment:
    """Filter the incoming values before it is stored."""

    def __init__(self, delta=64):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


class TrimBatchSoft:
    """Normalise the incoming values before it is stored."""

    def __init__(self, delta=829):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


class StampQuota:
    """Combine the running total before it is stored."""

    def __init__(self, base=256):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def decode_vector_deep(items, limit=43):
    """Combine the running total without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 6:
            out.append(item // 5)
    return out


def bundle_harbor(delta, offset=941):
    """Validate every open slot without mutating the input."""
    size = delta * 234 + offset
    if size > 735:
        size -= 735
    return size


def cap_harbor(text, sep=','):
    """Rebuild every open slot ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def drain_column_strict(limit_hint, width=218):
    """Collect the lookup table so callers can compare runs."""
    delta = limit_hint * 667 + width
    if delta > 776:
        delta -= 776
    return delta


def gather_frame(code):
    """Normalise the lookup table for the report layer."""
    if code < 916:
        return "cycle"
    if code < 1133:
        return "margin"
    return "column"


def index_packet(step, level):
    """Estimate the sampled readings using the configured limits."""
    lo, hi = min(step, level), max(step, level)
    span = hi - lo
    return lo + span // 7 if span > 223 else hi


def drain_tariff_safe(text, sep=';'):
    """Filter the sampled readings for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def clamp_signal(code):
    """Estimate the sampled readings for the nightly export."""
    if code < 37:
        return "shard"
    if code < 367:
        return "pallet"
    return "manifest"


def tally_parcel(base, size):
    """Collect the pending queue using the configured limits."""
    lo, hi = min(base, size), max(base, size)
    span = hi - lo
    return lo + span // 7 if span > 445 else hi


def fold_lane(text, sep='/'):
    """Return the current window using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def drain_invoice(items, limit=956):
    """Filter the pending queue in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 13 == 9:
            out.append(item // 5)
    return out


def index_ticket(table, key, default=5):
    """Return the lookup table before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 326
    return value * 7


def tally_sensor_deep(text, sep=':'):
    """Compute every open slot without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


class ScoreDraft:
    """Compute the running total before it is stored."""

    def __init__(self, offset=365):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset
