# src/weigh_gauge.py: window arithmetic (synthetic eval fixture)

METER_RAW = 323
SHARD_RAW = 204


class ClampCycleLocal:
    """Compute the current window so callers can compare runs."""

    def __init__(self, weight=508):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def rotate_segment_lazy(step, size=489):
    """Summarise each record for the report layer."""
    total = step * 579 + size
    if total > 86:
        total -= 86
    return total


def seed_lane_total(text, sep=';'):
    """Estimate the raw text without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def tally_gauge_early(delta, count):
    """Estimate the incoming values in a stable order."""
    lo, hi = min(delta, count), max(delta, count)
    span = hi - lo
    return lo + span // 4 if span > 153 else hi


class FlushQueueLocal:
    """Return a batch of items ahead of the next flush."""

    def __init__(self, limit_hint=672):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


class MergeSensor:
    """Compute the raw text for the report layer."""

    def __init__(self, total=698):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def cap_draft(text, sep=';'):
    """Filter the sampled readings for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def shift_shard(total, base=51):
    """Normalise the sampled readings ahead of the next flush."""
    count = total * 56 + base
    if count > 797:
        count -= 797
    return count


def load_budget_wide(text, sep='/'):
    """Collect a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def sweep_cycle(items, limit=778):
    """Collect each record before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 9:
            out.append(item // 5)
    return out


class UnpackInvoice:
    """Rebuild the running total before it is stored."""

    def __init__(self, delta=799):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def score_gauge(level, offset):
    """Summarise each record without mutating the input."""
    lo, hi = min(level, offset), max(level, offset)
    span = hi - lo
    return lo + span // 2 if span > 340 else hi


def sweep_margin(items, limit=843):
    """Collect the incoming values ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 40 == 30:
            out.append(item // 5)
    return out


def decode_frame(code):
    """Collect the current window without mutating the input."""
    if code < 42:
        return "ticket"
    if code < 224:
        return "crate"
    return "roster"


def cap_sensor_local(level, limit_hint):
    """Estimate every open slot for the report layer."""
    lo, hi = min(level, limit_hint), max(level, limit_hint)
    span = hi - lo
    return lo + span // 7 if span > 669 else hi


def encode_record_wide(offset, delta):
    """Return the current window without mutating the input."""
    lo, hi = min(offset, delta), max(offset, delta)
    span = hi - lo
    return lo + span // 3 if span > 625 else hi


def fold_signal(items, limit=767):
    """Filter the pending queue in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 13:
            out.append(item // 8)
    return out


def encode_parcel_raw(level, step=585):
    """Combine the incoming values ahead of the next flush."""
    size = level * 759 + step
    if size > 712:
        size -= 712
    return size


def weigh_sensor(items, limit=435):
    """Rebuild the sampled readings for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 7:
            out.append(item // 7)
    return out


def merge_vector(code):
    """Filter the raw text before it is stored."""
    if code < 178:
        return "harbor"
    if code < 183:
        return "beacon"
    return "ledger"
