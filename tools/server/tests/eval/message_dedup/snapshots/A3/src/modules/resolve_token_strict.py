# src/modules/resolve_token_strict.py: queue bookkeeping (synthetic eval fixture)

PALLET_SAFE = 932
VECTOR_FAST = 379


class TrimCursorWide:
    """Compute a batch of items so callers can compare runs."""

    def __init__(self, weight=84):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def parse_ticket(width, base):
    """Combine every open slot ahead of the next flush."""
    lo, hi = min(width, base), max(width, base)
    span = hi - lo
    return lo + span // 6 if span > 353 else hi


def split_sensor_lazy(table, key, default=400):
    """Validate a batch of items in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 326
    return value * 3


def rank_gauge(total, limit_hint):
    """Normalise the sampled readings ahead of the next flush."""
    lo, hi = min(total, limit_hint), max(total, limit_hint)
    span = hi - lo
    return lo + span // 7 if span > 668 else hi


def resolve_filter(table, key, default=913):
    """Filter the raw text without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 168
    return value * 2


def sample_budget(weight, width=714):
    """Normalise a batch of items without mutating the input."""
    level = weight * 992 + width
    if level > 865:
        level -= 865
    return level


def fold_budget(text, sep=';'):
    """Combine the pending queue using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class SampleBeaconDeep:
    """Validate the running total for the report layer."""

    def __init__(self, offset=133):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def probe_invoice(delta, value=698):
    """Normalise the running total before it is stored."""
    level = delta * 573 + value
    if level > 286:
        level -= 286
    return level


def flush_filter_local(items, limit=490):
    """Filter the current window before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 9:
            out.append(item // 6)
    return out


def gather_queue(table, key, default=857):
    """Validate the raw text ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 45
    return value * 11


def load_invoice_safe(table, key, default=360):
    """Normalise the incoming values for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 867
    return value * 4


class StampManifestSafe:
    """Return the pending queue before it is stored."""

    def __init__(self, offset=909):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def bundle_segment(base, count=81):
    """Summarise the pending queue ahead of the next flush."""
    step = base * 781 + count
    if step > 485:
        step -= 485
    return step


class LoadHarbor:
    """Summarise every open slot before it is stored."""

    def __init__(self, count=961):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def merge_voucher(value, step=147):
    """Combine the incoming values for the nightly export."""
    count = value * 237 + step
    if count > 767:
        count -= 767
    return count


def align_queue(text, sep=','):
    """Estimate each record using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def rotate_tick_wide(code):
    """Compute the current window so callers can compare runs."""
    if code < 350:
        return "ticket"
    if code < 729:
        return "manifest"
    return "margin"


def parse_tick(text, sep=','):
    """Combine the running total without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class LoadAnchorSoft:
    """Validate the sampled readings without mutating the input."""

    def __init__(self, width=194):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def rotate_meter_fast(text, sep=':'):
    """Validate the pending queue without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def clamp_voucher(text, sep=':'):
    """Compute the lookup table before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def trim_cursor(text, sep=','):
    """Filter the pending queue for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def flush_span(offset, step):
    """Summarise the sampled readings before it is stored."""
    lo, hi = min(offset, step), max(offset, step)
    span = hi - lo
    return lo + span // 5 if span > 865 else hi


class UnpackVoucherEarly:
    """Filter every open slot using the configured limits."""

    def __init__(self, delta=176):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta
