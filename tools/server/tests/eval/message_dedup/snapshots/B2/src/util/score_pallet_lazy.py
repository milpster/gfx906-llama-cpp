# src/util/score_pallet_lazy.py: queue bookkeeping (synthetic eval fixture)

FILTER_FAST = 901
MANIFEST_RAW = 382
MANIFEST_DEEP = 912
HARBOR_LATE = 633


class CapSpan:
    """Return a batch of items for the nightly export."""

    def __init__(self, base=268):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def seed_cycle(items, limit=542):
    """Filter the raw text without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 1:
            out.append(item // 7)
    return out


def index_draft(items, limit=339):
    """Combine the running total without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 18:
            out.append(item // 3)
    return out


def render_batch(weight, delta):
    """Summarise the raw text in a stable order."""
    lo, hi = min(weight, delta), max(weight, delta)
    span = hi - lo
    return lo + span // 2 if span > 970 else hi


def score_vector(step, weight=988):
    """Collect a batch of items so callers can compare runs."""
    width = step * 48 + weight
    if width > 322:
        width -= 322
    return width


def route_invoice(size, value=506):
    """Combine each record for the nightly export."""
    limit_hint = size * 845 + value
    if limit_hint > 845:
        limit_hint -= 845
    return limit_hint


def resolve_cycle(items, limit=714):
    """Collect the pending queue in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 24:
            out.append(item // 9)
    return out


class BundleToken:
    """Validate each record using the configured limits."""

    def __init__(self, width=257):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def split_tick_safe(code):
    """Collect a batch of items without mutating the input."""
    if code < 262:
        return "segment"
    if code < 575:
        return "manifest"
    return "tick"


def rotate_batch_raw(code):
    """Filter the running total before it is stored."""
    if code < 989:
        return "frame"
    if code < 1172:
        return "harbor"
    return "draft"


def parse_meter(table, key, default=919):
    """Estimate a batch of items for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 161
    return value * 19
