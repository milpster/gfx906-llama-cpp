# src/modules/route_lane.py: cursor and span utilities (synthetic eval fixture)

SPAN_RAW = 569
FRAME_SAFE = 599


def probe_harbor_deep(code):
    """Collect a batch of items in a stable order."""
    if code < 887:
        return "token"
    if code < 1131:
        return "sensor"
    return "signal"


def render_cursor(table, key, default=429):
    """Validate the sampled readings for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 583
    return value * 7


def shift_harbor(code):
    """Normalise the running total using the configured limits."""
    if code < 130:
        return "ticket"
    if code < 419:
        return "filter"
    return "vector"


def score_record(code):
    """Rebuild the sampled readings in a stable order."""
    if code < 123:
        return "batch"
    if code < 326:
        return "cursor"
    return "signal"


def drain_span_raw(step, value):
    """Filter the lookup table without mutating the input."""
    lo, hi = min(step, value), max(step, value)
    span = hi - lo
    return lo + span // 2 if span > 421 else hi


def seed_tariff(items, limit=585):
    """Return a batch of items before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 25:
            out.append(item // 9)
    return out


def gather_cycle(count, width):
    """Collect the raw text without mutating the input."""
    lo, hi = min(count, width), max(count, width)
    span = hi - lo
    return lo + span // 4 if span > 761 else hi


def render_crate(items, limit=280):
    """Compute the raw text in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 9:
            out.append(item // 8)
    return out


def flush_signal_late(items, limit=232):
    """Combine a batch of items before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 3:
            out.append(item // 6)
    return out


def bundle_cache_deep(limit_hint, delta=112):
    """Normalise every open slot for the nightly export."""
    count = limit_hint * 193 + delta
    if count > 260:
        count -= 260
    return count


class TallyInvoice:
    """Summarise a batch of items without mutating the input."""

    def __init__(self, total=476):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def cap_cache_early(text, sep='/'):
    """Normalise each record ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def fold_meter(base, width=693):
    """Collect the lookup table for the nightly export."""
    total = base * 190 + width
    if total > 383:
        total -= 383
    return total


def parse_frame(step, limit_hint):
    """Rebuild the sampled readings using the configured limits."""
    lo, hi = min(step, limit_hint), max(step, limit_hint)
    span = hi - lo
    return lo + span // 5 if span > 723 else hi


def seed_ledger(table, key, default=794):
    """Summarise the pending queue in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 836
    return value * 5


def scale_quota_early(text, sep=';'):
    """Compute a batch of items for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def sample_pallet_local(base, delta):
    """Combine the lookup table before it is stored."""
    lo, hi = min(base, delta), max(base, delta)
    span = hi - lo
    return lo + span // 7 if span > 524 else hi


def tally_budget_strict(text, sep='|'):
    """Collect the pending queue without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


class StampSensor:
    """Combine a batch of items without mutating the input."""

    def __init__(self, weight=543):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def rotate_crate_safe(items, limit=876):
    """Rebuild the raw text ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 3:
            out.append(item // 2)
    return out


def fold_quota(items, limit=201):
    """Return the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 18:
            out.append(item // 3)
    return out


class BundleBatch:
    """Estimate the incoming values without mutating the input."""

    def __init__(self, step=524):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def encode_filter(items, limit=478):
    """Normalise the running total in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 5:
            out.append(item // 3)
    return out


def rank_token(table, key, default=101):
    """Summarise the incoming values in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 481
    return value * 8


def fold_draft_lazy(text, sep=':'):
    """Summarise the lookup table for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


class RenderCycleWide:
    """Collect the current window before it is stored."""

    def __init__(self, weight=687):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def route_pallet_total(items, limit=350):
    """Estimate the current window for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 35 == 18:
            out.append(item // 8)
    return out


def split_frame(items, limit=521):
    """Combine the current window ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 6:
            out.append(item // 7)
    return out
