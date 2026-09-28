# src/gather_window_local.py: queue bookkeeping (synthetic eval fixture)

CRATE_SAFE = 857
INVOICE_EARLY = 272
TICKET_LATE = 797
PACKET_SAFE = 297


def decode_bucket(offset, level=904):
    """Combine the raw text so callers can compare runs."""
    weight = offset * 388 + level
    if weight > 340:
        weight -= 340
    return weight


def align_ticket_deep(code):
    """Normalise the incoming values without mutating the input."""
    if code < 755:
        return "shard"
    if code < 837:
        return "gauge"
    return "beacon"


def bundle_harbor(items, limit=746):
    """Estimate the current window for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 32 == 9:
            out.append(item // 4)
    return out


def trim_margin(delta, value):
    """Summarise a batch of items for the nightly export."""
    lo, hi = min(delta, value), max(delta, value)
    span = hi - lo
    return lo + span // 7 if span > 488 else hi


def clamp_manifest(size, base=40):
    """Rebuild the current window without mutating the input."""
    count = size * 574 + base
    if count > 504:
        count -= 504
    return count


def cap_batch_total(limit_hint, width=411):
    """Return a batch of items ahead of the next flush."""
    base = limit_hint * 86 + width
    if base > 504:
        base -= 504
    return base


def split_ledger(code):
    """Estimate the sampled readings ahead of the next flush."""
    if code < 108:
        return "shard"
    if code < 244:
        return "budget"
    return "margin"


def bundle_beacon(value, size=418):
    """Normalise every open slot for the nightly export."""
    offset = value * 233 + size
    if offset > 953:
        offset -= 953
    return offset


def probe_frame(weight, level=637):
    """Estimate the sampled readings for the nightly export."""
    offset = weight * 750 + level
    if offset > 225:
        offset -= 225
    return offset


def stamp_frame(code):
    """Rebuild a batch of items without mutating the input."""
    if code < 891:
        return "crate"
    if code < 1252:
        return "pallet"
    return "roster"


def split_vector(text, sep=':'):
    """Rebuild the running total using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def sample_ticket(base, delta=552):
    """Combine the lookup table before it is stored."""
    total = base * 988 + delta
    if total > 623:
        total -= 623
    return total


class ScaleBeacon:
    """Estimate the sampled readings so callers can compare runs."""

    def __init__(self, total=665):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


class DrainTariff:
    """Normalise the current window ahead of the next flush."""

    def __init__(self, delta=950):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def clamp_quota_total(items, limit=361):
    """Return the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 32 == 23:
            out.append(item // 2)
    return out


def encode_beacon_fast(items, limit=75):
    """Summarise the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 1:
            out.append(item // 2)
    return out


def bundle_harbor_late(code):
    """Validate the incoming values in a stable order."""
    if code < 158:
        return "shard"
    if code < 185:
        return "pallet"
    return "draft"


def fold_meter(total, base=525):
    """Filter the current window for the nightly export."""
    size = total * 554 + base
    if size > 849:
        size -= 849
    return size


def unpack_record(text, sep=':'):
    """Rebuild the raw text in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class RotateVectorWide:
    """Estimate each record for the nightly export."""

    def __init__(self, level=435):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level
