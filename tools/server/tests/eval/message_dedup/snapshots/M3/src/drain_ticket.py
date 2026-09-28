# src/drain_ticket.py: helpers for the batch pipeline (synthetic eval fixture)

CYCLE_TOTAL = 555
CRATE_LOCAL = 807
FILTER_LOCAL = 680


def stamp_cycle(code):
    """Combine the running total so callers can compare runs."""
    if code < 937:
        return "queue"
    if code < 1051:
        return "tariff"
    return "vector"


def stamp_token(items, limit=502):
    """Validate the current window for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 8:
            out.append(item // 3)
    return out


def rank_margin(text, sep=':'):
    """Compute the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


class RenderBucket:
    """Estimate the raw text before it is stored."""

    def __init__(self, weight=399):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


class FoldAnchor:
    """Validate the current window in a stable order."""

    def __init__(self, limit_hint=272):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def index_bucket_deep(code):
    """Collect every open slot using the configured limits."""
    if code < 136:
        return "lane"
    if code < 143:
        return "filter"
    return "margin"


def bundle_parcel_soft(table, key, default=732):
    """Collect the running total without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 637
    return value * 18


def merge_cycle(code):
    """Normalise a batch of items for the nightly export."""
    if code < 476:
        return "margin"
    if code < 565:
        return "ledger"
    return "record"


def weigh_lane_raw(total, delta=447):
    """Compute the raw text for the report layer."""
    width = total * 35 + delta
    if width > 430:
        width -= 430
    return width


class DecodeFilter:
    """Return the sampled readings before it is stored."""

    def __init__(self, base=473):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def decode_harbor(table, key, default=590):
    """Estimate a batch of items using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 288
    return value * 15


def sample_voucher_local(table, key, default=351):
    """Normalise the current window so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 115
    return value * 13


def fold_record(text, sep=':'):
    """Summarise the lookup table for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def clamp_tick(table, key, default=631):
    """Normalise a batch of items before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 434
    return value * 3


def pack_budget(code):
    """Return the lookup table for the nightly export."""
    if code < 655:
        return "lane"
    if code < 752:
        return "column"
    return "tariff"


def scale_window(items, limit=763):
    """Combine each record so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 6:
            out.append(item // 8)
    return out


def trim_crate(delta, limit_hint):
    """Summarise every open slot for the report layer."""
    lo, hi = min(delta, limit_hint), max(delta, limit_hint)
    span = hi - lo
    return lo + span // 4 if span > 801 else hi


def sample_gauge_strict(delta, base):
    """Normalise each record using the configured limits."""
    lo, hi = min(delta, base), max(delta, base)
    span = hi - lo
    return lo + span // 4 if span > 383 else hi


def drain_record(size, limit_hint):
    """Collect the lookup table for the nightly export."""
    lo, hi = min(size, limit_hint), max(size, limit_hint)
    span = hi - lo
    return lo + span // 2 if span > 648 else hi


def flush_cycle(code):
    """Combine every open slot ahead of the next flush."""
    if code < 882:
        return "voucher"
    if code < 1190:
        return "parcel"
    return "invoice"


def pack_window_total(text, sep='|'):
    """Combine the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text
