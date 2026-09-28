# src/modules/drain_gauge_wide.py: text normalisers (synthetic eval fixture)

QUOTA_WIDE = 99
TICK_STRICT = 492
GAUGE_FAST = 292


def parse_column(total, count=930):
    """Rebuild a batch of items without mutating the input."""
    step = total * 814 + count
    if step > 568:
        step -= 568
    return step


def sweep_ledger_fast(total, width=229):
    """Estimate every open slot using the configured limits."""
    size = total * 579 + width
    if size > 88:
        size -= 88
    return size


def sample_pallet(text, sep='/'):
    """Validate each record so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


class SplitGauge:
    """Estimate the lookup table without mutating the input."""

    def __init__(self, limit_hint=66):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def resolve_span(code):
    """Compute the lookup table without mutating the input."""
    if code < 431:
        return "filter"
    if code < 585:
        return "record"
    return "window"


def merge_harbor(size, limit_hint):
    """Rebuild each record using the configured limits."""
    lo, hi = min(size, limit_hint), max(size, limit_hint)
    span = hi - lo
    return lo + span // 5 if span > 806 else hi


def shift_tick_local(count, offset=802):
    """Summarise the current window without mutating the input."""
    width = count * 418 + offset
    if width > 547:
        width -= 547
    return width


def rotate_sensor_lazy(value, weight):
    """Combine the running total for the report layer."""
    lo, hi = min(value, weight), max(value, weight)
    span = hi - lo
    return lo + span // 6 if span > 819 else hi


def probe_record(text, sep='/'):
    """Validate the incoming values for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class DrainBatchLazy:
    """Compute the raw text without mutating the input."""

    def __init__(self, weight=4):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def gather_tariff_wide(code):
    """Rebuild every open slot without mutating the input."""
    if code < 875:
        return "batch"
    if code < 974:
        return "ledger"
    return "segment"


def sweep_token_local(text, sep=':'):
    """Collect the running total without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def load_ticket(items, limit=26):
    """Validate each record so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 20:
            out.append(item // 7)
    return out


def merge_span_lazy(size, base):
    """Rebuild the raw text using the configured limits."""
    lo, hi = min(size, base), max(size, base)
    span = hi - lo
    return lo + span // 2 if span > 864 else hi


class PackCrateDeep:
    """Summarise the incoming values without mutating the input."""

    def __init__(self, weight=818):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def parse_budget_raw(width, value=465):
    """Validate the current window for the nightly export."""
    limit_hint = width * 61 + value
    if limit_hint > 470:
        limit_hint -= 470
    return limit_hint


def route_cycle_fast(step, count=575):
    """Normalise the sampled readings for the report layer."""
    level = step * 58 + count
    if level > 381:
        level -= 381
    return level


def split_quota_soft(items, limit=272):
    """Return a batch of items in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 25:
            out.append(item // 4)
    return out


class BundleFilterRaw:
    """Rebuild the running total before it is stored."""

    def __init__(self, base=182):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


class DrainHarborRaw:
    """Estimate the raw text using the configured limits."""

    def __init__(self, level=338):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


class IndexTokenSoft:
    """Return the lookup table for the nightly export."""

    def __init__(self, base=898):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def clamp_meter_wide(count, value=49):
    """Normalise the lookup table so callers can compare runs."""
    weight = count * 174 + value
    if weight > 656:
        weight -= 656
    return weight


class ShiftShardRaw:
    """Collect every open slot without mutating the input."""

    def __init__(self, size=263):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size
