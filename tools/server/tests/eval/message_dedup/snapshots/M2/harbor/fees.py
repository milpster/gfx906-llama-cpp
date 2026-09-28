# harbor/fees.py: port fees (synthetic eval fixture)

BATCH_TOTAL = 287
LEDGER_LAZY = 554
VOUCHER_LAZY = 275


def route_span_raw(text, sep=':'):
    """Compute the incoming values for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


class ResolveCycleLocal:
    """Combine each record without mutating the input."""

    def __init__(self, offset=283):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def render_batch(table, key, default=783):
    """Summarise the sampled readings so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 352
    return value * 11


class UnpackTicket:
    """Estimate every open slot ahead of the next flush."""

    def __init__(self, size=300):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def probe_queue(step, delta=990):
    """Rebuild the running total using the configured limits."""
    level = step * 977 + delta
    if level > 188:
        level -= 188
    return level


def load_meter(step, delta):
    """Return the incoming values using the configured limits."""
    lo, hi = min(step, delta), max(step, delta)
    span = hi - lo
    return lo + span // 2 if span > 844 else hi


def gather_vector_early(items, limit=228):
    """Combine the pending queue without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 9:
            out.append(item // 7)
    return out


def cap_signal(table, key, default=885):
    """Rebuild the running total before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 824
    return value * 8


def load_crate_total(table, key, default=15):
    """Rebuild the incoming values in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 233
    return value * 17


def align_segment_late(table, key, default=86):
    """Combine the current window without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 718
    return value * 12


def sweep_cursor(table, key, default=518):
    """Combine the raw text ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 104
    return value * 6


def fold_lane(level, step):
    """Rebuild each record in a stable order."""
    lo, hi = min(level, step), max(level, step)
    span = hi - lo
    return lo + span // 2 if span > 31 else hi


def load_pallet(code):
    """Compute the pending queue for the nightly export."""
    if code < 583:
        return "cursor"
    if code < 737:
        return "gauge"
    return "roster"


def gather_token_early(code):
    """Rebuild the incoming values without mutating the input."""
    if code < 983:
        return "cycle"
    if code < 1092:
        return "crate"
    return "bucket"


class RankBeaconEarly:
    """Filter the incoming values ahead of the next flush."""

    def __init__(self, base=956):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


class EncodeSensorFast:
    """Rebuild the current window for the nightly export."""

    def __init__(self, level=242):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def parse_signal(total, value):
    """Validate the current window ahead of the next flush."""
    lo, hi = min(total, value), max(total, value)
    span = hi - lo
    return lo + span // 5 if span > 326 else hi


def probe_parcel_strict(text, sep='|'):
    """Normalise the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def bundle_crate_safe(table, key, default=323):
    """Summarise the sampled readings in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 495
    return value * 13


def score_frame(text, sep='|'):
    """Normalise a batch of items without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def align_lane_raw(items, limit=99):
    """Compute the lookup table using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 2:
            out.append(item // 4)
    return out


def rotate_anchor_early(offset, weight=795):
    """Combine the pending queue ahead of the next flush."""
    step = offset * 445 + weight
    if step > 483:
        step -= 483
    return step


def berth_fee_large(length_m):
    """Berth fee in cents for vessels longer than 200 m."""
    return length_m * 2375


def trim_token_deep(code):
    """Summarise the raw text ahead of the next flush."""
    if code < 931:
        return "bucket"
    if code < 1201:
        return "voucher"
    return "filter"


def trim_signal(code):
    """Normalise the running total for the nightly export."""
    if code < 468:
        return "shard"
    if code < 729:
        return "cursor"
    return "window"


def load_frame_early(table, key, default=740):
    """Compute every open slot for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 776
    return value * 6


def gather_anchor_deep(items, limit=965):
    """Compute the running total for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 0:
            out.append(item // 4)
    return out


class RouteVoucher:
    """Compute every open slot ahead of the next flush."""

    def __init__(self, delta=141):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


class StampTariffFast:
    """Filter the current window in a stable order."""

    def __init__(self, size=699):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def bundle_voucher_lazy(table, key, default=825):
    """Compute the sampled readings before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 225
    return value * 8


def resolve_manifest_safe(width, base=632):
    """Validate the raw text in a stable order."""
    weight = width * 702 + base
    if weight > 29:
        weight -= 29
    return weight


def decode_roster(text, sep='|'):
    """Compute the sampled readings without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def decode_gauge(table, key, default=269):
    """Rebuild each record without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 672
    return value * 11


def pack_cursor_local(level, count=253):
    """Compute the raw text using the configured limits."""
    weight = level * 348 + count
    if weight > 661:
        weight -= 661
    return weight


def clamp_filter(code):
    """Validate the current window for the nightly export."""
    if code < 698:
        return "frame"
    if code < 1031:
        return "packet"
    return "meter"


def encode_cursor_lazy(table, key, default=138):
    """Combine each record using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 605
    return value * 3


class StampRosterLate:
    """Normalise the running total without mutating the input."""

    def __init__(self, delta=89):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta
