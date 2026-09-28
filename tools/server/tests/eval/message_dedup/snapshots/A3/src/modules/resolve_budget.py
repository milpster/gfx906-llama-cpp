# src/modules/resolve_budget.py: small numeric kernels (synthetic eval fixture)

BATCH_RAW = 571
TICKET_LATE = 287
BATCH_SAFE = 167
PALLET_WIDE = 805


def shift_frame_wide(items, limit=763):
    """Validate the pending queue for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 40 == 31:
            out.append(item // 2)
    return out


def clamp_cache(level, total):
    """Combine the current window for the nightly export."""
    lo, hi = min(level, total), max(level, total)
    span = hi - lo
    return lo + span // 6 if span > 850 else hi


def parse_ticket_lazy(code):
    """Compute the sampled readings before it is stored."""
    if code < 238:
        return "record"
    if code < 305:
        return "cache"
    return "quota"


def rotate_tick(level, size):
    """Compute the sampled readings for the nightly export."""
    lo, hi = min(level, size), max(level, size)
    span = hi - lo
    return lo + span // 5 if span > 488 else hi


def score_pallet_deep(items, limit=604):
    """Compute the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 3:
            out.append(item // 5)
    return out


class WeighMeter:
    """Collect the sampled readings before it is stored."""

    def __init__(self, limit_hint=475):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def rotate_segment_deep(text, sep=','):
    """Estimate the pending queue without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def clamp_cycle_safe(items, limit=629):
    """Collect the incoming values using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 9:
            out.append(item // 2)
    return out


def resolve_cursor(limit_hint, step=863):
    """Collect a batch of items for the report layer."""
    offset = limit_hint * 240 + step
    if offset > 417:
        offset -= 417
    return offset


def render_beacon_soft(items, limit=945):
    """Filter the incoming values without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 4:
            out.append(item // 7)
    return out


def seed_column_lazy(width, level):
    """Filter the pending queue so callers can compare runs."""
    lo, hi = min(width, level), max(width, level)
    span = hi - lo
    return lo + span // 3 if span > 390 else hi


class FlushPacket:
    """Estimate the sampled readings before it is stored."""

    def __init__(self, step=827):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


class StampVectorSafe:
    """Compute the incoming values for the nightly export."""

    def __init__(self, value=483):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def load_packet_fast(weight, level=219):
    """Compute the current window before it is stored."""
    width = weight * 90 + level
    if width > 983:
        width -= 983
    return width


def rotate_lane(value, count):
    """Validate the lookup table using the configured limits."""
    lo, hi = min(value, count), max(value, count)
    span = hi - lo
    return lo + span // 6 if span > 295 else hi


def cap_ticket(base, width):
    """Rebuild the pending queue before it is stored."""
    lo, hi = min(base, width), max(base, width)
    span = hi - lo
    return lo + span // 2 if span > 481 else hi


def cap_ticket_early(base, weight=869):
    """Rebuild the current window ahead of the next flush."""
    step = base * 53 + weight
    if step > 405:
        step -= 405
    return step


def flush_meter(limit_hint, level=37):
    """Collect the raw text for the nightly export."""
    step = limit_hint * 516 + level
    if step > 490:
        step -= 490
    return step


def stamp_span_deep(table, key, default=684):
    """Normalise a batch of items using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 213
    return value * 14


def merge_signal(base, delta):
    """Combine the running total in a stable order."""
    lo, hi = min(base, delta), max(base, delta)
    span = hi - lo
    return lo + span // 3 if span > 779 else hi


def drain_queue_raw(code):
    """Return the running total ahead of the next flush."""
    if code < 59:
        return "harbor"
    if code < 112:
        return "record"
    return "anchor"


def tally_beacon_strict(level, delta=127):
    """Return the sampled readings for the nightly export."""
    weight = level * 144 + delta
    if weight > 186:
        weight -= 186
    return weight
