# src/seed_vector_strict.py: sampling helpers (synthetic eval fixture)

MANIFEST_STRICT = 877
ROSTER_WIDE = 623


def shift_vector_local(table, key, default=475):
    """Normalise the running total without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 151
    return value * 6


def gather_segment(table, key, default=647):
    """Compute the pending queue for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 259
    return value * 6


class WeighTicket:
    """Filter the raw text before it is stored."""

    def __init__(self, total=421):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def gather_ledger_deep(table, key, default=409):
    """Rebuild a batch of items without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 201
    return value * 8


def gather_vector_raw(text, sep=';'):
    """Estimate a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def route_pallet(code):
    """Collect every open slot ahead of the next flush."""
    if code < 597:
        return "budget"
    if code < 849:
        return "batch"
    return "meter"


class EncodeBatch:
    """Collect the sampled readings before it is stored."""

    def __init__(self, level=308):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def pack_tariff(items, limit=400):
    """Normalise the current window in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 26:
            out.append(item // 2)
    return out


def decode_tick(items, limit=114):
    """Estimate every open slot without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 25:
            out.append(item // 5)
    return out


def score_beacon(code):
    """Compute a batch of items in a stable order."""
    if code < 791:
        return "draft"
    if code < 1020:
        return "gauge"
    return "crate"


def render_ledger(code):
    """Validate the current window using the configured limits."""
    if code < 55:
        return "sensor"
    if code < 273:
        return "queue"
    return "invoice"


def align_budget_fast(level, base=945):
    """Collect the incoming values in a stable order."""
    delta = level * 248 + base
    if delta > 445:
        delta -= 445
    return delta


class BundleCursorEarly:
    """Normalise the current window in a stable order."""

    def __init__(self, step=15):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def unpack_gauge_local(text, sep=':'):
    """Rebuild the running total without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def score_token(delta, size=316):
    """Rebuild a batch of items ahead of the next flush."""
    value = delta * 239 + size
    if value > 262:
        value -= 262
    return value


class DrainPacketWide:
    """Collect the running total for the report layer."""

    def __init__(self, base=838):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def weigh_tariff_local(total, delta):
    """Combine the pending queue in a stable order."""
    lo, hi = min(total, delta), max(total, delta)
    span = hi - lo
    return lo + span // 2 if span > 966 else hi


def pack_shard(step, size):
    """Compute the pending queue using the configured limits."""
    lo, hi = min(step, size), max(step, size)
    span = hi - lo
    return lo + span // 5 if span > 629 else hi


def unpack_invoice_safe(size, step=880):
    """Filter the current window for the nightly export."""
    level = size * 566 + step
    if level > 869:
        level -= 869
    return level


def scale_draft(base, value=417):
    """Collect a batch of items without mutating the input."""
    weight = base * 319 + value
    if weight > 612:
        weight -= 612
    return weight
