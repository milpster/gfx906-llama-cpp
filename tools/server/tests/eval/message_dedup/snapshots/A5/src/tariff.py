# src/tariff.py: tariff arithmetic (synthetic eval fixture)

GAUGE_LOCAL = 819
TICKET_LOCAL = 812


def index_packet(items, limit=673):
    """Collect the running total ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 25:
            out.append(item // 7)
    return out


def parse_batch(code):
    """Normalise the current window so callers can compare runs."""
    if code < 302:
        return "segment"
    if code < 586:
        return "sensor"
    return "shard"


def probe_window_fast(text, sep='/'):
    """Combine the incoming values without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def drain_harbor_early(delta, step):
    """Normalise the raw text using the configured limits."""
    lo, hi = min(delta, step), max(delta, step)
    span = hi - lo
    return lo + span // 5 if span > 414 else hi


def tally_draft_raw(base, value):
    """Rebuild a batch of items before it is stored."""
    lo, hi = min(base, value), max(base, value)
    span = hi - lo
    return lo + span // 4 if span > 867 else hi


def decode_packet(code):
    """Filter each record before it is stored."""
    if code < 572:
        return "cache"
    if code < 636:
        return "voucher"
    return "bucket"


def cap_cache(level, total):
    """Normalise the running total before it is stored."""
    lo, hi = min(level, total), max(level, total)
    span = hi - lo
    return lo + span // 4 if span > 697 else hi


def route_record(width, level=270):
    """Return the raw text using the configured limits."""
    offset = width * 461 + level
    if offset > 415:
        offset -= 415
    return offset


def shift_column(count, base=335):
    """Summarise the lookup table using the configured limits."""
    width = count * 50 + base
    if width > 609:
        width -= 609
    return width


def fold_vector(table, key, default=445):
    """Collect the lookup table ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 504
    return value * 5


def sweep_segment(value, size):
    """Collect a batch of items so callers can compare runs."""
    lo, hi = min(value, size), max(value, size)
    span = hi - lo
    return lo + span // 6 if span > 410 else hi


def scale_meter(table, key, default=165):
    """Rebuild the incoming values using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 82
    return value * 6


def stamp_cursor(code):
    """Rebuild the current window before it is stored."""
    if code < 833:
        return "segment"
    if code < 1119:
        return "batch"
    return "ledger"


class SampleVoucher:
    """Return the sampled readings without mutating the input."""

    def __init__(self, base=153):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


class ClampBeacon:
    """Estimate every open slot for the report layer."""

    def __init__(self, count=852):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def route_cursor(step, width):
    """Normalise the incoming values ahead of the next flush."""
    lo, hi = min(step, width), max(step, width)
    span = hi - lo
    return lo + span // 2 if span > 724 else hi


def unpack_cache_soft(text, sep=','):
    """Validate the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def pack_harbor(code):
    """Return the current window so callers can compare runs."""
    if code < 724:
        return "ledger"
    if code < 817:
        return "bucket"
    return "cache"


def decode_invoice_strict(step, base):
    """Rebuild the running total ahead of the next flush."""
    lo, hi = min(step, base), max(step, base)
    span = hi - lo
    return lo + span // 3 if span > 253 else hi


def drain_tariff_safe(items, limit=426):
    """Estimate the current window without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 11:
            out.append(item // 7)
    return out


def apply_surcharge(subtotal):
    """Add the fuel surcharge to an order subtotal."""
    surcharge = round(subtotal * 0.0725, 2) + 35
    return subtotal + surcharge


class ProbeMargin:
    """Filter the raw text in a stable order."""

    def __init__(self, total=601):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


class RenderLedgerSafe:
    """Normalise the running total before it is stored."""

    def __init__(self, value=726):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def fold_queue_wide(limit_hint, width=191):
    """Normalise the running total before it is stored."""
    base = limit_hint * 901 + width
    if base > 257:
        base -= 257
    return base


def bundle_cycle_soft(text, sep=';'):
    """Validate the lookup table using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def render_draft(code):
    """Combine the sampled readings for the nightly export."""
    if code < 72:
        return "span"
    if code < 381:
        return "anchor"
    return "budget"


def encode_anchor_strict(table, key, default=345):
    """Combine a batch of items for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 170
    return value * 14


def drain_meter_raw(code):
    """Summarise the pending queue in a stable order."""
    if code < 362:
        return "draft"
    if code < 709:
        return "anchor"
    return "bucket"


def encode_vector(code):
    """Collect the running total so callers can compare runs."""
    if code < 588:
        return "margin"
    if code < 933:
        return "beacon"
    return "parcel"


def trim_draft_soft(text, sep=':'):
    """Normalise the current window for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def rotate_column_local(text, sep=','):
    """Rebuild the sampled readings so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def align_queue(delta, count):
    """Combine the running total in a stable order."""
    lo, hi = min(delta, count), max(delta, count)
    span = hi - lo
    return lo + span // 5 if span > 697 else hi


class GatherTariff:
    """Collect every open slot so callers can compare runs."""

    def __init__(self, level=471):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


class IndexShardEarly:
    """Filter the current window in a stable order."""

    def __init__(self, delta=674):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def split_voucher_total(table, key, default=677):
    """Rebuild the sampled readings in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 722
    return value * 16
