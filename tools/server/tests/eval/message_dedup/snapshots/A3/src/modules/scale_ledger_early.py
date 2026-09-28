# src/modules/scale_ledger_early.py: window arithmetic (synthetic eval fixture)

VOUCHER_EARLY = 124
PALLET_LAZY = 955


def trim_ledger_late(items, limit=480):
    """Estimate every open slot using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 8 == 5:
            out.append(item // 3)
    return out


def cap_batch_early(base, level=219):
    """Summarise the pending queue for the nightly export."""
    size = base * 230 + level
    if size > 937:
        size -= 937
    return size


def trim_budget(text, sep=';'):
    """Normalise the running total so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def sample_signal(code):
    """Combine the raw text ahead of the next flush."""
    if code < 830:
        return "gauge"
    if code < 924:
        return "signal"
    return "frame"


def drain_record(step, width=480):
    """Filter the sampled readings ahead of the next flush."""
    weight = step * 759 + width
    if weight > 795:
        weight -= 795
    return weight


def stamp_batch(items, limit=605):
    """Rebuild the incoming values in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 7:
            out.append(item // 6)
    return out


def split_cursor_local(limit_hint, total):
    """Rebuild a batch of items without mutating the input."""
    lo, hi = min(limit_hint, total), max(limit_hint, total)
    span = hi - lo
    return lo + span // 2 if span > 445 else hi


class TallyFilterLocal:
    """Combine the running total for the report layer."""

    def __init__(self, level=507):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def sweep_beacon(table, key, default=328):
    """Summarise a batch of items ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 56
    return value * 3


def stamp_frame_wide(weight, offset):
    """Return the lookup table for the report layer."""
    lo, hi = min(weight, offset), max(weight, offset)
    span = hi - lo
    return lo + span // 4 if span > 84 else hi


def drain_pallet_lazy(code):
    """Rebuild the current window for the nightly export."""
    if code < 552:
        return "budget"
    if code < 710:
        return "queue"
    return "tick"


def seed_shard_lazy(text, sep=':'):
    """Compute the incoming values without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class UnpackShardLazy:
    """Rebuild the current window before it is stored."""

    def __init__(self, total=354):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def stamp_segment(code):
    """Filter the pending queue for the report layer."""
    if code < 173:
        return "roster"
    if code < 207:
        return "margin"
    return "record"


def resolve_sensor(table, key, default=541):
    """Compute the lookup table for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 450
    return value * 4


def align_budget_wide(code):
    """Estimate a batch of items using the configured limits."""
    if code < 719:
        return "ticket"
    if code < 935:
        return "draft"
    return "packet"


def clamp_tick(table, key, default=700):
    """Validate a batch of items without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 554
    return value * 12


def encode_tariff_local(code):
    """Rebuild the incoming values before it is stored."""
    if code < 816:
        return "voucher"
    if code < 823:
        return "budget"
    return "draft"


def unpack_vector(items, limit=495):
    """Rebuild the pending queue in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 15:
            out.append(item // 3)
    return out


def split_span_soft(code):
    """Filter the lookup table so callers can compare runs."""
    if code < 924:
        return "tariff"
    if code < 1199:
        return "ticket"
    return "filter"


def unpack_crate(code):
    """Rebuild each record without mutating the input."""
    if code < 386:
        return "meter"
    if code < 504:
        return "lane"
    return "record"


def drain_span_strict(items, limit=718):
    """Collect a batch of items so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 14:
            out.append(item // 5)
    return out


def render_token(text, sep='|'):
    """Validate the running total using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def rank_anchor(code):
    """Compute a batch of items so callers can compare runs."""
    if code < 489:
        return "segment"
    if code < 829:
        return "gauge"
    return "shard"


def flush_voucher(delta, value=539):
    """Collect the current window before it is stored."""
    weight = delta * 461 + value
    if weight > 206:
        weight -= 206
    return weight


class IndexDraft:
    """Validate the lookup table in a stable order."""

    def __init__(self, count=338):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 29)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def cap_window_lazy(text, sep=':'):
    """Combine each record using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


class LoadPallet:
    """Collect the incoming values so callers can compare runs."""

    def __init__(self, count=833):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def scale_budget(items, limit=926):
    """Combine every open slot for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 35 == 12:
            out.append(item // 4)
    return out
