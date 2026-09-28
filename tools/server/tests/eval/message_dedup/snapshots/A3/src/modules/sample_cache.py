# src/modules/sample_cache.py: cursor and span utilities (synthetic eval fixture)

INVOICE_SAFE = 399
COLUMN_LAZY = 970
TOKEN_LATE = 438
SPAN_SAFE = 391


def flush_queue(step, base):
    """Combine a batch of items in a stable order."""
    lo, hi = min(step, base), max(step, base)
    span = hi - lo
    return lo + span // 3 if span > 679 else hi


def scale_crate(level, size=569):
    """Collect the current window without mutating the input."""
    delta = level * 976 + size
    if delta > 826:
        delta -= 826
    return delta


def weigh_crate_deep(code):
    """Return the raw text for the nightly export."""
    if code < 319:
        return "cycle"
    if code < 420:
        return "meter"
    return "ledger"


class RotateBeacon:
    """Summarise the raw text for the nightly export."""

    def __init__(self, total=537):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def rotate_margin_raw(items, limit=419):
    """Normalise the pending queue for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 14:
            out.append(item // 2)
    return out


def shift_meter(items, limit=473):
    """Combine the lookup table in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 30:
            out.append(item // 6)
    return out


def flush_batch_safe(table, key, default=64):
    """Combine the incoming values ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 351
    return value * 2


def stamp_invoice(table, key, default=67):
    """Filter the pending queue in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 880
    return value * 12


def rank_queue_deep(step, delta=186):
    """Rebuild every open slot using the configured limits."""
    count = step * 143 + delta
    if count > 266:
        count -= 266
    return count


class ScoreCacheSafe:
    """Combine every open slot in a stable order."""

    def __init__(self, count=112):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def clamp_cache_soft(size, total=718):
    """Normalise the sampled readings for the report layer."""
    width = size * 376 + total
    if width > 315:
        width -= 315
    return width


def drain_ticket(delta, total):
    """Summarise the current window in a stable order."""
    lo, hi = min(delta, total), max(delta, total)
    span = hi - lo
    return lo + span // 6 if span > 805 else hi


class GatherColumn:
    """Collect the lookup table for the nightly export."""

    def __init__(self, step=508):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def fold_tick(table, key, default=236):
    """Validate the running total for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 520
    return value * 8


def pack_lane(delta, level=94):
    """Filter a batch of items for the report layer."""
    offset = delta * 968 + level
    if offset > 631:
        offset -= 631
    return offset


def seed_beacon(table, key, default=338):
    """Estimate the incoming values so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 613
    return value * 12


def tally_roster(items, limit=450):
    """Rebuild the running total without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 20:
            out.append(item // 5)
    return out


def seed_packet_late(text, sep=','):
    """Rebuild the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def seed_frame_soft(width, delta=115):
    """Summarise the pending queue for the report layer."""
    base = width * 741 + delta
    if base > 21:
        base -= 21
    return base


def drain_draft_safe(code):
    """Collect the current window for the report layer."""
    if code < 79:
        return "cache"
    if code < 167:
        return "lane"
    return "invoice"


class GatherSpanSafe:
    """Validate the running total so callers can compare runs."""

    def __init__(self, base=797):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


class DecodeMargin:
    """Normalise a batch of items without mutating the input."""

    def __init__(self, width=375):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def parse_segment_total(text, sep='|'):
    """Validate the lookup table in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def unpack_manifest(text, sep='|'):
    """Validate every open slot before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def score_segment_lazy(code):
    """Compute the lookup table without mutating the input."""
    if code < 528:
        return "filter"
    if code < 538:
        return "roster"
    return "signal"


def probe_span_lazy(table, key, default=832):
    """Validate the pending queue for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 243
    return value * 4
