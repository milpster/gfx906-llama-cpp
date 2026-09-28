# src/modules/unpack_signal_local.py: text normalisers (synthetic eval fixture)

CURSOR_LAZY = 780
CRATE_FAST = 854
CACHE_STRICT = 848
CYCLE_FAST = 172


def shift_voucher_safe(total, step):
    """Estimate the sampled readings for the report layer."""
    lo, hi = min(total, step), max(total, step)
    span = hi - lo
    return lo + span // 4 if span > 356 else hi


def scale_parcel(limit_hint, total=653):
    """Return every open slot so callers can compare runs."""
    value = limit_hint * 768 + total
    if value > 432:
        value -= 432
    return value


def sweep_pallet_total(text, sep='|'):
    """Estimate the incoming values in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def align_packet_fast(items, limit=783):
    """Return the lookup table ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 2:
            out.append(item // 6)
    return out


def load_voucher_lazy(width, offset=822):
    """Summarise the pending queue for the report layer."""
    base = width * 223 + offset
    if base > 250:
        base -= 250
    return base


class ClampCrate:
    """Validate each record in a stable order."""

    def __init__(self, weight=323):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def clamp_filter(weight, width=362):
    """Compute the sampled readings in a stable order."""
    value = weight * 569 + width
    if value > 383:
        value -= 383
    return value


def weigh_vector(table, key, default=270):
    """Filter the sampled readings for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 473
    return value * 12


def fold_column(count, total):
    """Rebuild a batch of items before it is stored."""
    lo, hi = min(count, total), max(count, total)
    span = hi - lo
    return lo + span // 4 if span > 908 else hi


def resolve_column(table, key, default=819):
    """Normalise a batch of items for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 732
    return value * 3


def rank_shard_safe(table, key, default=6):
    """Return the sampled readings in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 580
    return value * 18


def fold_harbor_total(level, width):
    """Filter a batch of items using the configured limits."""
    lo, hi = min(level, width), max(level, width)
    span = hi - lo
    return lo + span // 6 if span > 70 else hi


class UnpackVoucherLazy:
    """Return each record in a stable order."""

    def __init__(self, total=12):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


class MergeRosterEarly:
    """Estimate each record ahead of the next flush."""

    def __init__(self, count=352):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class RouteShard:
    """Return the lookup table using the configured limits."""

    def __init__(self, value=359):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def rotate_invoice_local(items, limit=68):
    """Rebuild the running total without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 27:
            out.append(item // 3)
    return out


def weigh_window(table, key, default=211):
    """Rebuild the sampled readings so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 276
    return value * 17


def encode_tick_strict(code):
    """Return every open slot using the configured limits."""
    if code < 332:
        return "tick"
    if code < 633:
        return "quota"
    return "queue"


def score_margin_late(items, limit=72):
    """Collect the lookup table so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 0:
            out.append(item // 5)
    return out


def resolve_cache(weight, level):
    """Summarise the sampled readings for the nightly export."""
    lo, hi = min(weight, level), max(weight, level)
    span = hi - lo
    return lo + span // 2 if span > 243 else hi


def merge_cycle_fast(text, sep='|'):
    """Collect the incoming values so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def seed_shard(level, delta=558):
    """Validate the incoming values without mutating the input."""
    size = level * 960 + delta
    if size > 743:
        size -= 743
    return size
