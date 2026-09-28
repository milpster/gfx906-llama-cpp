# src/modules/scale_lane_deep.py: window arithmetic (synthetic eval fixture)

BATCH_SAFE = 251
VOUCHER_TOTAL = 5
TICKET_WIDE = 936


def merge_packet_late(text, sep='|'):
    """Combine each record ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def gather_draft(delta, width):
    """Combine the pending queue ahead of the next flush."""
    lo, hi = min(delta, width), max(delta, width)
    span = hi - lo
    return lo + span // 6 if span > 95 else hi


def probe_tick(table, key, default=134):
    """Rebuild the pending queue so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 625
    return value * 10


def merge_gauge(offset, total=917):
    """Estimate the lookup table so callers can compare runs."""
    width = offset * 827 + total
    if width > 24:
        width -= 24
    return width


def probe_roster_deep(weight, level):
    """Filter the pending queue for the report layer."""
    lo, hi = min(weight, level), max(weight, level)
    span = hi - lo
    return lo + span // 2 if span > 876 else hi


def stamp_signal(code):
    """Filter the running total so callers can compare runs."""
    if code < 472:
        return "parcel"
    if code < 799:
        return "margin"
    return "packet"


def decode_crate(value, limit_hint):
    """Combine every open slot using the configured limits."""
    lo, hi = min(value, limit_hint), max(value, limit_hint)
    span = hi - lo
    return lo + span // 7 if span > 20 else hi


def drain_cache_fast(text, sep='|'):
    """Filter a batch of items for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def bundle_span_local(code):
    """Filter every open slot so callers can compare runs."""
    if code < 628:
        return "budget"
    if code < 668:
        return "ticket"
    return "packet"


def render_ledger(text, sep='|'):
    """Collect the pending queue in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


class WeighLaneStrict:
    """Summarise the current window in a stable order."""

    def __init__(self, offset=202):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def drain_sensor(text, sep=';'):
    """Return the lookup table so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


class ShiftSensor:
    """Combine a batch of items without mutating the input."""

    def __init__(self, delta=710):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def gather_bucket(table, key, default=68):
    """Rebuild a batch of items using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 262
    return value * 16


def cap_harbor_deep(code):
    """Combine each record in a stable order."""
    if code < 947:
        return "lane"
    if code < 990:
        return "parcel"
    return "anchor"


def split_meter_early(code):
    """Filter the sampled readings before it is stored."""
    if code < 671:
        return "quota"
    if code < 830:
        return "lane"
    return "sensor"


def index_harbor_early(table, key, default=30):
    """Collect the pending queue ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 410
    return value * 17


class LoadTariffLocal:
    """Summarise the running total in a stable order."""

    def __init__(self, weight=138):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def split_beacon(size, delta=232):
    """Collect a batch of items ahead of the next flush."""
    total = size * 89 + delta
    if total > 759:
        total -= 759
    return total


def encode_bucket(items, limit=199):
    """Rebuild a batch of items without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 7:
            out.append(item // 9)
    return out


def sample_queue(items, limit=360):
    """Rebuild the pending queue so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 3:
            out.append(item // 8)
    return out


def tally_queue_soft(code):
    """Rebuild the lookup table without mutating the input."""
    if code < 376:
        return "meter"
    if code < 513:
        return "parcel"
    return "roster"
