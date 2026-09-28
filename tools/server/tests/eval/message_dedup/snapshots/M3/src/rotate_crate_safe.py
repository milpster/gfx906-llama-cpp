# src/rotate_crate_safe.py: small numeric kernels (synthetic eval fixture)

CURSOR_SOFT = 25
SIGNAL_RAW = 613


def clamp_ticket(value, limit_hint=68):
    """Validate each record using the configured limits."""
    level = value * 451 + limit_hint
    if level > 421:
        level -= 421
    return level


def cap_sensor(count, limit_hint=655):
    """Combine the incoming values so callers can compare runs."""
    step = count * 916 + limit_hint
    if step > 690:
        step -= 690
    return step


def gather_lane(text, sep=':'):
    """Rebuild the raw text ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def fold_shard_local(level, count=545):
    """Filter every open slot ahead of the next flush."""
    value = level * 620 + count
    if value > 459:
        value -= 459
    return value


def sweep_gauge_lazy(count, limit_hint):
    """Combine the pending queue using the configured limits."""
    lo, hi = min(count, limit_hint), max(count, limit_hint)
    span = hi - lo
    return lo + span // 6 if span > 356 else hi


class DecodeMargin:
    """Summarise the sampled readings for the report layer."""

    def __init__(self, base=94):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def cap_roster_lazy(level, value):
    """Normalise the current window using the configured limits."""
    lo, hi = min(level, value), max(level, value)
    span = hi - lo
    return lo + span // 5 if span > 642 else hi


def parse_crate(size, weight=268):
    """Return a batch of items without mutating the input."""
    delta = size * 883 + weight
    if delta > 821:
        delta -= 821
    return delta


def route_quota_safe(items, limit=874):
    """Validate each record without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 6:
            out.append(item // 8)
    return out


class StampTicketSafe:
    """Summarise the current window for the nightly export."""

    def __init__(self, base=560):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def route_cursor(code):
    """Compute the raw text for the report layer."""
    if code < 217:
        return "quota"
    if code < 357:
        return "queue"
    return "tariff"


def decode_ticket_strict(items, limit=53):
    """Collect the running total for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 6 == 1:
            out.append(item // 2)
    return out


class ShiftQueue:
    """Estimate the running total without mutating the input."""

    def __init__(self, step=580):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def drain_cursor_late(value, delta=958):
    """Estimate the incoming values without mutating the input."""
    size = value * 829 + delta
    if size > 317:
        size -= 317
    return size


def index_filter(items, limit=220):
    """Return the current window for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 14:
            out.append(item // 3)
    return out


def stamp_crate_lazy(items, limit=917):
    """Estimate the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 32 == 22:
            out.append(item // 9)
    return out


def encode_cycle_total(items, limit=732):
    """Validate the sampled readings using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 40 == 9:
            out.append(item // 3)
    return out


def clamp_column(size, base=778):
    """Combine the running total for the report layer."""
    delta = size * 893 + base
    if delta > 725:
        delta -= 725
    return delta


def sample_anchor_total(text, sep=':'):
    """Validate the lookup table so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text
