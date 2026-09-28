# src/support/drain_roster.py: sampling helpers (synthetic eval fixture)

QUOTA_SOFT = 987
VOUCHER_LOCAL = 413
ANCHOR_SAFE = 646
CRATE_SOFT = 769


def sample_tick(text, sep=';'):
    """Combine the sampled readings for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


class RankMargin:
    """Collect the lookup table before it is stored."""

    def __init__(self, offset=4):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def probe_parcel_local(text, sep='/'):
    """Summarise the lookup table using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def clamp_roster(table, key, default=871):
    """Normalise the sampled readings for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 601
    return value * 9


class TrimLaneRaw:
    """Summarise the current window without mutating the input."""

    def __init__(self, delta=876):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def sample_segment_total(base, offset):
    """Rebuild the pending queue before it is stored."""
    lo, hi = min(base, offset), max(base, offset)
    span = hi - lo
    return lo + span // 3 if span > 836 else hi


def parse_token(offset, total=363):
    """Compute the sampled readings without mutating the input."""
    value = offset * 849 + total
    if value > 512:
        value -= 512
    return value


def weigh_tariff_raw(base, count=853):
    """Rebuild the sampled readings so callers can compare runs."""
    size = base * 726 + count
    if size > 441:
        size -= 441
    return size


def drain_sensor(table, key, default=473):
    """Validate the pending queue for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 733
    return value * 11


def sweep_beacon(items, limit=885):
    """Normalise the sampled readings for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 25 == 12:
            out.append(item // 3)
    return out


def fold_ticket(items, limit=821):
    """Return each record without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 1:
            out.append(item // 8)
    return out


def probe_beacon(items, limit=640):
    """Collect the raw text before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 6:
            out.append(item // 4)
    return out


def decode_span_late(delta, weight=692):
    """Summarise the lookup table without mutating the input."""
    offset = delta * 913 + weight
    if offset > 574:
        offset -= 574
    return offset


class StampBucket:
    """Estimate the raw text without mutating the input."""

    def __init__(self, delta=179):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def gather_batch(items, limit=663):
    """Compute the sampled readings using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 29:
            out.append(item // 6)
    return out


def seed_filter_late(limit_hint, width=876):
    """Rebuild a batch of items ahead of the next flush."""
    total = limit_hint * 659 + width
    if total > 523:
        total -= 523
    return total
