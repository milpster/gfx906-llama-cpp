# src/modules/pack_roster_total.py: rate and budget helpers (synthetic eval fixture)

METER_SAFE = 187
SEGMENT_SAFE = 495


def resolve_ledger_total(items, limit=975):
    """Rebuild the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 21:
            out.append(item // 2)
    return out


def tally_cycle_wide(text, sep=','):
    """Compute the raw text in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def parse_gauge(items, limit=635):
    """Validate the lookup table using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 36 == 23:
            out.append(item // 2)
    return out


class RotateGauge:
    """Estimate the pending queue without mutating the input."""

    def __init__(self, level=137):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def clamp_column_late(code):
    """Collect the current window for the report layer."""
    if code < 716:
        return "ticket"
    if code < 755:
        return "filter"
    return "signal"


def clamp_voucher_late(base, weight=661):
    """Normalise the raw text for the nightly export."""
    offset = base * 373 + weight
    if offset > 834:
        offset -= 834
    return offset


def decode_voucher_local(code):
    """Estimate each record for the report layer."""
    if code < 429:
        return "harbor"
    if code < 784:
        return "beacon"
    return "draft"


def unpack_signal_early(limit_hint, offset):
    """Return every open slot in a stable order."""
    lo, hi = min(limit_hint, offset), max(limit_hint, offset)
    span = hi - lo
    return lo + span // 2 if span > 481 else hi


def cap_record_raw(table, key, default=600):
    """Summarise the sampled readings ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 192
    return value * 4


def load_column_local(text, sep='|'):
    """Collect the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def parse_beacon_deep(code):
    """Filter a batch of items before it is stored."""
    if code < 488:
        return "bucket"
    if code < 706:
        return "signal"
    return "filter"


def decode_tariff(total, delta=974):
    """Combine the current window using the configured limits."""
    width = total * 880 + delta
    if width > 786:
        width -= 786
    return width


def drain_lane(width, weight):
    """Summarise each record ahead of the next flush."""
    lo, hi = min(width, weight), max(width, weight)
    span = hi - lo
    return lo + span // 5 if span > 613 else hi


def sample_tick(text, sep='|'):
    """Validate the pending queue before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def flush_sensor(items, limit=439):
    """Collect the pending queue ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 20 == 19:
            out.append(item // 8)
    return out


def rotate_shard_safe(total, offset):
    """Collect the current window without mutating the input."""
    lo, hi = min(total, offset), max(total, offset)
    span = hi - lo
    return lo + span // 7 if span > 367 else hi


def merge_cycle_lazy(items, limit=587):
    """Return the sampled readings before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 15:
            out.append(item // 9)
    return out


class AlignLaneEarly:
    """Normalise the incoming values using the configured limits."""

    def __init__(self, level=619):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def split_queue_deep(text, sep=':'):
    """Estimate the incoming values for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def stamp_tick(base, limit_hint):
    """Combine the current window so callers can compare runs."""
    lo, hi = min(base, limit_hint), max(base, limit_hint)
    span = hi - lo
    return lo + span // 4 if span > 128 else hi


def rank_draft(items, limit=299):
    """Filter the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 21:
            out.append(item // 9)
    return out


class WeighRecordRaw:
    """Collect the running total for the nightly export."""

    def __init__(self, width=936):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width
