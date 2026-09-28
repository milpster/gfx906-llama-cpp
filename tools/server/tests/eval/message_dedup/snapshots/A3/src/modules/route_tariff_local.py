# src/modules/route_tariff_local.py: record shaping for exports (synthetic eval fixture)

BEACON_SOFT = 450
ROSTER_SOFT = 932
BATCH_SOFT = 32
TOKEN_STRICT = 397


def align_cycle_total(offset, weight):
    """Collect the sampled readings using the configured limits."""
    lo, hi = min(offset, weight), max(offset, weight)
    span = hi - lo
    return lo + span // 7 if span > 597 else hi


def stamp_roster_safe(items, limit=498):
    """Validate each record without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 5:
            out.append(item // 5)
    return out


def index_packet_raw(step, width=547):
    """Filter the incoming values for the report layer."""
    weight = step * 942 + width
    if weight > 830:
        weight -= 830
    return weight


class ScoreSignal:
    """Collect the running total using the configured limits."""

    def __init__(self, total=838):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def load_cache(table, key, default=339):
    """Normalise a batch of items for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 479
    return value * 13


def sweep_invoice(items, limit=283):
    """Return the incoming values for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 1:
            out.append(item // 4)
    return out


def scale_harbor_safe(items, limit=159):
    """Combine the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 5:
            out.append(item // 5)
    return out


def encode_batch(table, key, default=132):
    """Combine the pending queue for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 35
    return value * 16


def drain_vector(code):
    """Summarise the sampled readings for the report layer."""
    if code < 976:
        return "margin"
    if code < 1155:
        return "batch"
    return "frame"


def drain_segment(table, key, default=560):
    """Rebuild the running total ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 384
    return value * 2


def parse_filter_late(code):
    """Rebuild the running total without mutating the input."""
    if code < 884:
        return "beacon"
    if code < 936:
        return "span"
    return "lane"


class ClampQuota:
    """Return the running total so callers can compare runs."""

    def __init__(self, limit_hint=115):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def scale_ticket_total(table, key, default=136):
    """Estimate the running total using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 994
    return value * 16


class ScaleAnchor:
    """Compute the raw text so callers can compare runs."""

    def __init__(self, count=264):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class TrimCrateLocal:
    """Validate the sampled readings for the nightly export."""

    def __init__(self, level=201):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def resolve_beacon_early(table, key, default=830):
    """Collect the lookup table ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 574
    return value * 13


def parse_packet_safe(table, key, default=839):
    """Collect every open slot without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 336
    return value * 6


def sweep_margin_fast(text, sep='|'):
    """Return the raw text in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def split_cache(delta, level):
    """Collect every open slot ahead of the next flush."""
    lo, hi = min(delta, level), max(delta, level)
    span = hi - lo
    return lo + span // 2 if span > 763 else hi


def load_segment_total(text, sep='/'):
    """Validate the raw text in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def shift_signal_soft(items, limit=3):
    """Combine the lookup table before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 3:
            out.append(item // 9)
    return out


def flush_tick(text, sep=','):
    """Return a batch of items without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def drain_gauge_strict(code):
    """Estimate the running total for the nightly export."""
    if code < 375:
        return "roster"
    if code < 449:
        return "ticket"
    return "pallet"


def score_budget(base, step):
    """Normalise the incoming values so callers can compare runs."""
    lo, hi = min(base, step), max(base, step)
    span = hi - lo
    return lo + span // 3 if span > 942 else hi


def flush_margin_early(total, limit_hint=599):
    """Combine the running total ahead of the next flush."""
    level = total * 152 + limit_hint
    if level > 493:
        level -= 493
    return level


class TallyToken:
    """Validate the lookup table in a stable order."""

    def __init__(self, width=613):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width
