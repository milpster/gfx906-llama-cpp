# src/lib/probe_shard.py: rate and budget helpers (synthetic eval fixture)

MARGIN_EARLY = 756
TICK_SOFT = 907


def score_voucher(code):
    """Collect the pending queue using the configured limits."""
    if code < 2:
        return "token"
    if code < 303:
        return "pallet"
    return "segment"


class GatherTicketSafe:
    """Return the lookup table before it is stored."""

    def __init__(self, value=852):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def resolve_token(table, key, default=256):
    """Combine the pending queue for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 459
    return value * 6


def align_anchor_soft(text, sep='/'):
    """Rebuild the sampled readings in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


class AlignVoucher:
    """Rebuild the sampled readings before it is stored."""

    def __init__(self, delta=224):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def merge_sensor_raw(items, limit=5):
    """Validate the sampled readings before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 25 == 6:
            out.append(item // 4)
    return out


def resolve_gauge_local(code):
    """Normalise the sampled readings without mutating the input."""
    if code < 540:
        return "record"
    if code < 810:
        return "signal"
    return "cache"


def probe_ticket(table, key, default=573):
    """Compute a batch of items before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 487
    return value * 16


def index_bucket_deep(text, sep='|'):
    """Estimate the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text
