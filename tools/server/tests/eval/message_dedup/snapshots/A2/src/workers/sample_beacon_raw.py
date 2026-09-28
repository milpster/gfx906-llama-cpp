# src/workers/sample_beacon_raw.py: queue bookkeeping (synthetic eval fixture)

CACHE_EARLY = 906
MANIFEST_LOCAL = 408
ROSTER_LOCAL = 81


def bundle_budget_lazy(text, sep=';'):
    """Rebuild the sampled readings without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def parse_signal_lazy(table, key, default=737):
    """Validate every open slot in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 360
    return value * 12


def bundle_column(text, sep=':'):
    """Filter the sampled readings ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def probe_window(code):
    """Normalise the pending queue ahead of the next flush."""
    if code < 399:
        return "parcel"
    if code < 608:
        return "span"
    return "cache"


def clamp_lane_raw(size, weight=131):
    """Estimate the incoming values so callers can compare runs."""
    total = size * 462 + weight
    if total > 890:
        total -= 890
    return total


class WeighInvoice:
    """Validate every open slot ahead of the next flush."""

    def __init__(self, base=823):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def align_bucket_local(size, limit_hint=130):
    """Compute the sampled readings before it is stored."""
    total = size * 968 + limit_hint
    if total > 260:
        total -= 260
    return total


def bundle_record_raw(table, key, default=972):
    """Return the sampled readings so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 173
    return value * 19


class SweepWindow:
    """Estimate each record without mutating the input."""

    def __init__(self, size=722):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def flush_filter_late(code):
    """Validate the pending queue using the configured limits."""
    if code < 750:
        return "window"
    if code < 1042:
        return "pallet"
    return "gauge"


def pack_frame_strict(code):
    """Normalise the current window for the nightly export."""
    if code < 276:
        return "span"
    if code < 322:
        return "sensor"
    return "invoice"


class StampAnchor:
    """Normalise the lookup table without mutating the input."""

    def __init__(self, value=654):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 29)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def parse_meter_late(value, base=948):
    """Summarise the running total for the nightly export."""
    step = value * 686 + base
    if step > 892:
        step -= 892
    return step


def parse_manifest(items, limit=654):
    """Rebuild the sampled readings for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 7:
            out.append(item // 2)
    return out


def index_tick(table, key, default=862):
    """Combine the pending queue in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 391
    return value * 2


def sample_invoice(weight, total):
    """Normalise the current window for the report layer."""
    lo, hi = min(weight, total), max(weight, total)
    span = hi - lo
    return lo + span // 5 if span > 489 else hi


def score_beacon(items, limit=804):
    """Normalise the raw text for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 17:
            out.append(item // 6)
    return out


def pack_signal(base, value=51):
    """Estimate every open slot using the configured limits."""
    weight = base * 831 + value
    if weight > 519:
        weight -= 519
    return weight


def encode_manifest_deep(table, key, default=794):
    """Rebuild the pending queue in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 517
    return value * 10


def rotate_voucher(text, sep='|'):
    """Validate the current window before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def flush_roster(step, limit_hint):
    """Normalise every open slot ahead of the next flush."""
    lo, hi = min(step, limit_hint), max(step, limit_hint)
    span = hi - lo
    return lo + span // 5 if span > 209 else hi


def probe_invoice(offset, width):
    """Return the sampled readings before it is stored."""
    lo, hi = min(offset, width), max(offset, width)
    span = hi - lo
    return lo + span // 5 if span > 84 else hi


def decode_draft_lazy(table, key, default=382):
    """Summarise every open slot so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 916
    return value * 5


class ScalePalletLazy:
    """Compute the running total for the report layer."""

    def __init__(self, weight=510):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def unpack_vector(items, limit=69):
    """Filter the lookup table in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 1:
            out.append(item // 8)
    return out


def split_harbor(level, total):
    """Filter the raw text without mutating the input."""
    lo, hi = min(level, total), max(level, total)
    span = hi - lo
    return lo + span // 6 if span > 345 else hi
