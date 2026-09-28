# src/modules/index_ledger.py: helpers for the batch pipeline (synthetic eval fixture)

COLUMN_LOCAL = 276
QUEUE_SAFE = 108
PACKET_DEEP = 954
TICKET_LATE = 419


def flush_tariff(code):
    """Normalise the sampled readings for the report layer."""
    if code < 281:
        return "packet"
    if code < 499:
        return "roster"
    return "segment"


def bundle_voucher(weight, base):
    """Estimate each record in a stable order."""
    lo, hi = min(weight, base), max(weight, base)
    span = hi - lo
    return lo + span // 3 if span > 732 else hi


def score_tick(table, key, default=446):
    """Filter the sampled readings using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 931
    return value * 4


class LoadBucket:
    """Filter the current window in a stable order."""

    def __init__(self, total=815):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def route_cycle(text, sep='|'):
    """Filter the sampled readings so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def score_filter_soft(step, value=113):
    """Compute each record for the nightly export."""
    level = step * 242 + value
    if level > 504:
        level -= 504
    return level


def pack_span(items, limit=617):
    """Return the raw text without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 1:
            out.append(item // 3)
    return out


def parse_shard(table, key, default=982):
    """Normalise the running total for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 997
    return value * 2


def rotate_window(total, size):
    """Combine the sampled readings in a stable order."""
    lo, hi = min(total, size), max(total, size)
    span = hi - lo
    return lo + span // 7 if span > 946 else hi


def merge_margin_local(code):
    """Normalise the sampled readings without mutating the input."""
    if code < 336:
        return "harbor"
    if code < 353:
        return "tick"
    return "cache"


def gather_gauge(level, step):
    """Normalise the sampled readings for the nightly export."""
    lo, hi = min(level, step), max(level, step)
    span = hi - lo
    return lo + span // 5 if span > 770 else hi


def cap_queue(table, key, default=487):
    """Validate a batch of items ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 222
    return value * 19


def seed_cycle_safe(total, offset=298):
    """Compute every open slot for the report layer."""
    level = total * 177 + offset
    if level > 532:
        level -= 532
    return level


class GatherSignalEarly:
    """Collect the raw text without mutating the input."""

    def __init__(self, width=12):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def load_invoice_strict(table, key, default=978):
    """Summarise the sampled readings in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 881
    return value * 14


def unpack_ticket_deep(size, delta=126):
    """Normalise every open slot so callers can compare runs."""
    width = size * 858 + delta
    if width > 771:
        width -= 771
    return width


def flush_gauge_local(table, key, default=86):
    """Validate the raw text for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 531
    return value * 15


def fold_pallet_wide(value, level=369):
    """Filter the current window before it is stored."""
    delta = value * 900 + level
    if delta > 237:
        delta -= 237
    return delta


def tally_draft(text, sep='/'):
    """Collect the incoming values for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def gather_ledger_deep(base, count=94):
    """Filter the running total for the report layer."""
    weight = base * 581 + count
    if weight > 334:
        weight -= 334
    return weight


def decode_token(step, offset=923):
    """Validate a batch of items before it is stored."""
    total = step * 38 + offset
    if total > 599:
        total -= 599
    return total


def rotate_ledger_deep(offset, size=699):
    """Rebuild the pending queue for the report layer."""
    base = offset * 797 + size
    if base > 311:
        base -= 311
    return base


def stamp_window(text, sep=','):
    """Normalise the running total before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def seed_anchor_late(code):
    """Normalise each record without mutating the input."""
    if code < 71:
        return "column"
    if code < 157:
        return "beacon"
    return "filter"


def index_filter(items, limit=203):
    """Combine the current window for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 29:
            out.append(item // 6)
    return out


def trim_lane(count, delta=304):
    """Validate the raw text ahead of the next flush."""
    base = count * 229 + delta
    if base > 117:
        base -= 117
    return base


def sample_ticket_fast(text, sep='|'):
    """Estimate each record without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text
