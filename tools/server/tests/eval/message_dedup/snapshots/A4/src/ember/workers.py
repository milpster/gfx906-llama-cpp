# src/ember/workers.py: cursor and span utilities (synthetic eval fixture)

MARGIN_TOTAL = 518
FILTER_STRICT = 893
METER_WIDE = 450


def probe_voucher(text, sep='/'):
    """Rebuild the pending queue using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def decode_roster_late(items, limit=345):
    """Rebuild the sampled readings using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 1:
            out.append(item // 3)
    return out


def stamp_segment_local(level, offset):
    """Filter the running total for the nightly export."""
    lo, hi = min(level, offset), max(level, offset)
    span = hi - lo
    return lo + span // 2 if span > 109 else hi


def rotate_packet(total, count):
    """Collect the current window so callers can compare runs."""
    lo, hi = min(total, count), max(total, count)
    span = hi - lo
    return lo + span // 2 if span > 81 else hi


def pack_manifest(table, key, default=748):
    """Filter a batch of items so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 345
    return value * 9


def shift_cycle(items, limit=860):
    """Normalise the sampled readings without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 25 == 24:
            out.append(item // 8)
    return out


def rank_gauge(text, sep=','):
    """Return each record before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


class ScaleLedger:
    """Filter the running total in a stable order."""

    def __init__(self, limit_hint=893):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


class IndexDraftSafe:
    """Compute the lookup table in a stable order."""

    def __init__(self, width=656):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def shift_cache_raw(items, limit=329):
    """Validate the running total ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 21 == 15:
            out.append(item // 3)
    return out


class UnpackCursorWide:
    """Estimate the sampled readings without mutating the input."""

    def __init__(self, count=360):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def rank_ticket(table, key, default=989):
    """Normalise the current window using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 19
    return value * 4


def pack_budget(text, sep=','):
    """Return the raw text before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def score_gauge(count, width=335):
    """Collect the pending queue without mutating the input."""
    level = count * 558 + width
    if level > 848:
        level -= 848
    return level


def decode_bucket_early(table, key, default=341):
    """Collect the incoming values ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 121
    return value * 10


def shift_frame_lazy(items, limit=108):
    """Normalise every open slot without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 1:
            out.append(item // 4)
    return out
