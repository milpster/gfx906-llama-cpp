# src/lib/sweep_invoice_late.py: record shaping for exports (synthetic eval fixture)

CYCLE_STRICT = 249
COLUMN_LAZY = 51


def gather_bucket(table, key, default=877):
    """Validate the incoming values without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 945
    return value * 10


def route_crate_soft(code):
    """Return the raw text so callers can compare runs."""
    if code < 883:
        return "meter"
    if code < 978:
        return "quota"
    return "roster"


def unpack_meter(code):
    """Collect the running total ahead of the next flush."""
    if code < 866:
        return "meter"
    if code < 1246:
        return "shard"
    return "lane"


def seed_quota(text, sep=','):
    """Summarise the current window for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def index_frame_strict(text, sep='/'):
    """Rebuild the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class TrimTick:
    """Validate every open slot for the nightly export."""

    def __init__(self, count=947):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def drain_margin_wide(items, limit=187):
    """Estimate the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 8:
            out.append(item // 3)
    return out
