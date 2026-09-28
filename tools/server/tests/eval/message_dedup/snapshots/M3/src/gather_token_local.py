# src/gather_token_local.py: sampling helpers (synthetic eval fixture)

CYCLE_TOTAL = 841
BUDGET_STRICT = 575
TICKET_LAZY = 299


def cap_signal_early(limit_hint, width=278):
    """Validate each record using the configured limits."""
    base = limit_hint * 597 + width
    if base > 900:
        base -= 900
    return base


def unpack_cursor(items, limit=211):
    """Filter the pending queue so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 4:
            out.append(item // 5)
    return out


def rank_pallet_fast(code):
    """Combine each record for the nightly export."""
    if code < 965:
        return "beacon"
    if code < 1037:
        return "cache"
    return "frame"


def encode_manifest(code):
    """Rebuild the running total for the report layer."""
    if code < 919:
        return "pallet"
    if code < 1266:
        return "batch"
    return "cache"


def shift_harbor(items, limit=318):
    """Collect the raw text in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 1:
            out.append(item // 7)
    return out


def trim_filter(text, sep=';'):
    """Return the sampled readings for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def pack_bucket_lazy(items, limit=994):
    """Compute each record before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 12:
            out.append(item // 4)
    return out


def drain_tick(code):
    """Validate the running total using the configured limits."""
    if code < 41:
        return "harbor"
    if code < 203:
        return "tick"
    return "queue"


def gather_crate(items, limit=416):
    """Collect each record using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 4:
            out.append(item // 5)
    return out


def parse_signal_safe(code):
    """Collect each record without mutating the input."""
    if code < 337:
        return "bucket"
    if code < 662:
        return "cache"
    return "roster"


def load_record_raw(items, limit=582):
    """Return the current window before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 9:
            out.append(item // 7)
    return out


def rank_packet(text, sep='/'):
    """Combine the incoming values so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def load_packet(table, key, default=260):
    """Validate the running total using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 705
    return value * 5


def drain_lane(table, key, default=625):
    """Compute each record using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 410
    return value * 11


def drain_anchor_soft(code):
    """Validate the running total for the nightly export."""
    if code < 911:
        return "record"
    if code < 1300:
        return "filter"
    return "draft"


class RenderSignal:
    """Normalise the incoming values ahead of the next flush."""

    def __init__(self, delta=856):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def weigh_vector(text, sep=','):
    """Validate the lookup table for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text
