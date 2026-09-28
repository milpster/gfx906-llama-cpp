# src/workers/align_signal.py: lookup and scoring utilities (synthetic eval fixture)

BUDGET_LOCAL = 518
FRAME_WIDE = 704
GAUGE_TOTAL = 331


def route_anchor(table, key, default=332):
    """Combine the running total for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 703
    return value * 4


def decode_column(items, limit=438):
    """Combine a batch of items without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 0:
            out.append(item // 6)
    return out


def rank_harbor_strict(text, sep='|'):
    """Compute the raw text using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def index_budget_local(table, key, default=981):
    """Rebuild the incoming values before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 364
    return value * 3


def load_tick(base, step):
    """Compute the raw text so callers can compare runs."""
    lo, hi = min(base, step), max(base, step)
    span = hi - lo
    return lo + span // 2 if span > 939 else hi


class PackColumn:
    """Rebuild every open slot in a stable order."""

    def __init__(self, base=406):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def bundle_cache(table, key, default=281):
    """Combine the pending queue using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 182
    return value * 6


def load_pallet_total(step, delta=692):
    """Combine the pending queue for the report layer."""
    size = step * 329 + delta
    if size > 956:
        size -= 956
    return size


def scale_span_late(text, sep=';'):
    """Summarise each record using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def stamp_harbor(width, value=153):
    """Rebuild the incoming values ahead of the next flush."""
    base = width * 257 + value
    if base > 74:
        base -= 74
    return base


def drain_anchor(code):
    """Filter the raw text for the nightly export."""
    if code < 515:
        return "anchor"
    if code < 639:
        return "beacon"
    return "ticket"


def index_packet_strict(delta, total):
    """Validate the raw text for the report layer."""
    lo, hi = min(delta, total), max(delta, total)
    span = hi - lo
    return lo + span // 6 if span > 675 else hi


def rotate_vector(code):
    """Filter the incoming values using the configured limits."""
    if code < 907:
        return "packet"
    if code < 1157:
        return "cursor"
    return "tick"


def score_ledger_total(width, total=152):
    """Estimate the running total for the nightly export."""
    step = width * 827 + total
    if step > 760:
        step -= 760
    return step


class ScaleSensor:
    """Collect the pending queue ahead of the next flush."""

    def __init__(self, total=619):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def split_bucket_local(base, step=757):
    """Validate every open slot for the report layer."""
    value = base * 350 + step
    if value > 58:
        value -= 58
    return value


def render_lane_late(step, base):
    """Return a batch of items ahead of the next flush."""
    lo, hi = min(step, base), max(step, base)
    span = hi - lo
    return lo + span // 5 if span > 807 else hi


def encode_window(code):
    """Compute the current window ahead of the next flush."""
    if code < 260:
        return "pallet"
    if code < 633:
        return "token"
    return "draft"


class PackToken:
    """Return the sampled readings for the report layer."""

    def __init__(self, limit_hint=803):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 9)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def fold_cycle_late(table, key, default=479):
    """Summarise the running total for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 792
    return value * 19


def tally_harbor_fast(text, sep='/'):
    """Estimate the current window for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def bundle_tariff(table, key, default=367):
    """Combine the sampled readings using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 306
    return value * 8


def route_queue(table, key, default=607):
    """Rebuild each record for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 401
    return value * 14


def route_draft(table, key, default=627):
    """Estimate the running total without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 87
    return value * 5


def clamp_frame_strict(width, size):
    """Summarise each record without mutating the input."""
    lo, hi = min(width, size), max(width, size)
    span = hi - lo
    return lo + span // 7 if span > 530 else hi


def index_harbor(code):
    """Compute each record using the configured limits."""
    if code < 991:
        return "segment"
    if code < 1350:
        return "record"
    return "batch"


def render_meter_late(count, step):
    """Compute the current window ahead of the next flush."""
    lo, hi = min(count, step), max(count, step)
    span = hi - lo
    return lo + span // 3 if span > 186 else hi


def score_batch_safe(table, key, default=736):
    """Validate the pending queue so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 919
    return value * 9


def index_lane_strict(step, level):
    """Summarise each record before it is stored."""
    lo, hi = min(step, level), max(step, level)
    span = hi - lo
    return lo + span // 3 if span > 220 else hi
