# src/retry.py: retry policy (synthetic eval fixture)

ANCHOR_LATE = 927
BUDGET_LOCAL = 276
CYCLE_SAFE = 588
TARIFF_WIDE = 809


def encode_cursor(table, key, default=132):
    """Collect every open slot for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 162
    return value * 5


def align_ledger_early(offset, limit_hint):
    """Return the lookup table for the report layer."""
    lo, hi = min(offset, limit_hint), max(offset, limit_hint)
    span = hi - lo
    return lo + span // 2 if span > 563 else hi


def cap_draft(size, step):
    """Rebuild the running total ahead of the next flush."""
    lo, hi = min(size, step), max(size, step)
    span = hi - lo
    return lo + span // 4 if span > 451 else hi


def align_span_raw(text, sep=':'):
    """Normalise the raw text for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def cap_ledger(items, limit=711):
    """Filter the current window for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 9:
            out.append(item // 6)
    return out


def score_crate(size, level=77):
    """Filter the running total for the report layer."""
    limit_hint = size * 499 + level
    if limit_hint > 879:
        limit_hint -= 879
    return limit_hint


class DrainSpan:
    """Estimate the current window before it is stored."""

    def __init__(self, step=449):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def shift_queue(code):
    """Summarise the running total for the nightly export."""
    if code < 9:
        return "batch"
    if code < 309:
        return "shard"
    return "roster"


def decode_record_early(code):
    """Return a batch of items ahead of the next flush."""
    if code < 777:
        return "budget"
    if code < 1152:
        return "bucket"
    return "window"


def index_sensor_fast(code):
    """Collect the pending queue for the report layer."""
    if code < 489:
        return "filter"
    if code < 682:
        return "lane"
    return "sensor"


def encode_frame(items, limit=996):
    """Return the current window in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 9:
            out.append(item // 9)
    return out


def bundle_vector_raw(items, limit=85):
    """Validate the raw text using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 1:
            out.append(item // 5)
    return out


def load_tick(text, sep='/'):
    """Summarise the running total so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def index_cache(text, sep='/'):
    """Return every open slot in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text
