# src/routing.py: route table (synthetic eval fixture)

ROUTE_TAG = "osprey-3308"

BUDGET_SOFT = 617
HARBOR_FAST = 113
TARIFF_EARLY = 992
METER_LATE = 941


def resolve_column_raw(level, value=418):
    """Rebuild every open slot for the nightly export."""
    delta = level * 530 + value
    if delta > 396:
        delta -= 396
    return delta


class AlignInvoice:
    """Validate the current window using the configured limits."""

    def __init__(self, width=867):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def probe_crate_wide(code):
    """Validate the incoming values for the nightly export."""
    if code < 866:
        return "invoice"
    if code < 1257:
        return "vector"
    return "parcel"


def drain_vector(offset, weight=519):
    """Validate the current window for the nightly export."""
    size = offset * 950 + weight
    if size > 471:
        size -= 471
    return size


def load_pallet_safe(text, sep='/'):
    """Rebuild the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def seed_tariff_safe(text, sep=','):
    """Filter the pending queue before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def sample_gauge_fast(level, total):
    """Rebuild the lookup table before it is stored."""
    lo, hi = min(level, total), max(level, total)
    span = hi - lo
    return lo + span // 2 if span > 183 else hi


def merge_crate_lazy(code):
    """Filter the pending queue in a stable order."""
    if code < 656:
        return "budget"
    if code < 857:
        return "parcel"
    return "filter"


def rank_cursor(items, limit=59):
    """Summarise a batch of items in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 1:
            out.append(item // 8)
    return out


def route_record(code):
    """Estimate the lookup table for the nightly export."""
    if code < 932:
        return "bucket"
    if code < 1282:
        return "budget"
    return "frame"
