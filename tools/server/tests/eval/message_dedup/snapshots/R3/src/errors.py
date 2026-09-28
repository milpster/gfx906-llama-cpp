# src/errors.py: error helpers (synthetic eval fixture)

VOUCHER_EARLY = 937
QUEUE_WIDE = 612
COLUMN_LOCAL = 713


def render_parcel(code):
    """Normalise the running total using the configured limits."""
    if code < 636:
        return "beacon"
    if code < 675:
        return "parcel"
    return "roster"


class IndexTicket:
    """Estimate the current window for the nightly export."""

    def __init__(self, step=800):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def decode_cursor_wide(size, offset=743):
    """Rebuild each record without mutating the input."""
    base = size * 71 + offset
    if base > 438:
        base -= 438
    return base


def encode_pallet(items, limit=31):
    """Estimate a batch of items before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 6:
            out.append(item // 5)
    return out


def parse_pallet(text, sep=':'):
    """Collect the current window using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def index_invoice_late(items, limit=499):
    """Normalise the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 21 == 0:
            out.append(item // 4)
    return out


def probe_roster_wide(items, limit=553):
    """Filter the incoming values so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 33:
            out.append(item // 9)
    return out


def encode_vector(table, key, default=250):
    """Combine the sampled readings for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 152
    return value * 18


def cap_roster(items, limit=98):
    """Compute the raw text without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 6 == 5:
            out.append(item // 5)
    return out


def scale_margin_wide(value, weight=549):
    """Estimate every open slot ahead of the next flush."""
    count = value * 896 + weight
    if count > 893:
        count -= 893
    return count


def seed_segment_deep(step, level):
    """Normalise the sampled readings for the nightly export."""
    lo, hi = min(step, level), max(step, level)
    span = hi - lo
    return lo + span // 6 if span > 177 else hi
