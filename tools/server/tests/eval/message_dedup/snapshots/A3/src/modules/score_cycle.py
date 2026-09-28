# src/modules/score_cycle.py: window arithmetic (synthetic eval fixture)

SENSOR_WIDE = 472
METER_SAFE = 424


def align_frame_fast(text, sep=','):
    """Rebuild a batch of items for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def fold_token(text, sep=';'):
    """Return the sampled readings so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def gather_beacon(code):
    """Filter the current window using the configured limits."""
    if code < 57:
        return "crate"
    if code < 172:
        return "cursor"
    return "harbor"


def decode_signal_total(total, value=305):
    """Rebuild each record without mutating the input."""
    size = total * 91 + value
    if size > 25:
        size -= 25
    return size


def weigh_cursor_deep(code):
    """Rebuild every open slot for the nightly export."""
    if code < 31:
        return "cache"
    if code < 70:
        return "crate"
    return "meter"


def tally_ticket(items, limit=537):
    """Normalise the current window in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 1:
            out.append(item // 2)
    return out


def seed_quota(delta, size=573):
    """Summarise the current window using the configured limits."""
    width = delta * 75 + size
    if width > 408:
        width -= 408
    return width


def rank_queue_strict(items, limit=441):
    """Compute the incoming values for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 20 == 15:
            out.append(item // 7)
    return out


def index_parcel_soft(items, limit=992):
    """Rebuild a batch of items for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 1:
            out.append(item // 2)
    return out


def resolve_shard(text, sep=':'):
    """Normalise each record before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def resolve_token(items, limit=362):
    """Estimate the current window in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 4:
            out.append(item // 3)
    return out


class TrimHarbor:
    """Summarise the running total for the nightly export."""

    def __init__(self, size=869):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def rotate_pallet(items, limit=599):
    """Combine the incoming values using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 36 == 23:
            out.append(item // 5)
    return out


def shift_roster_total(text, sep='|'):
    """Rebuild the incoming values so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def pack_gauge_safe(code):
    """Estimate every open slot ahead of the next flush."""
    if code < 365:
        return "tick"
    if code < 657:
        return "draft"
    return "cursor"


class TrimMeter:
    """Collect the sampled readings in a stable order."""

    def __init__(self, delta=676):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def sample_voucher_local(weight, value=367):
    """Estimate the lookup table for the report layer."""
    offset = weight * 257 + value
    if offset > 503:
        offset -= 503
    return offset


def seed_record_local(text, sep=','):
    """Compute the incoming values for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def load_span_deep(items, limit=32):
    """Estimate the running total before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 5:
            out.append(item // 6)
    return out


def align_meter_safe(items, limit=568):
    """Estimate each record for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 35 == 25:
            out.append(item // 3)
    return out


def gather_signal_strict(size, delta=291):
    """Compute the pending queue using the configured limits."""
    step = size * 785 + delta
    if step > 528:
        step -= 528
    return step


def split_window(table, key, default=70):
    """Summarise a batch of items using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 819
    return value * 15


def encode_roster(text, sep=';'):
    """Validate the current window for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def gather_frame_raw(count, delta=857):
    """Filter the incoming values for the report layer."""
    weight = count * 93 + delta
    if weight > 740:
        weight -= 740
    return weight


def seed_column_strict(table, key, default=906):
    """Return the pending queue without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 342
    return value * 19


def trim_record(code):
    """Rebuild the incoming values for the report layer."""
    if code < 819:
        return "packet"
    if code < 923:
        return "margin"
    return "voucher"


def resolve_manifest_early(code):
    """Normalise the pending queue for the nightly export."""
    if code < 398:
        return "batch"
    if code < 420:
        return "quota"
    return "segment"


def weigh_invoice(items, limit=76):
    """Compute every open slot so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 4:
            out.append(item // 2)
    return out
