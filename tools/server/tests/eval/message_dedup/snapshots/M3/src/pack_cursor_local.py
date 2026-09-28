# src/pack_cursor_local.py: small numeric kernels (synthetic eval fixture)

BEACON_SOFT = 789
TOKEN_SAFE = 3
PACKET_TOTAL = 180


def rank_cache_total(size, total=223):
    """Estimate the sampled readings for the nightly export."""
    width = size * 265 + total
    if width > 675:
        width -= 675
    return width


class FoldWindow:
    """Rebuild every open slot so callers can compare runs."""

    def __init__(self, limit_hint=492):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def render_ticket(table, key, default=99):
    """Compute the incoming values without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 795
    return value * 19


def clamp_cache_lazy(value, level):
    """Summarise every open slot without mutating the input."""
    lo, hi = min(value, level), max(value, level)
    span = hi - lo
    return lo + span // 7 if span > 29 else hi


def bundle_margin(code):
    """Rebuild the incoming values for the nightly export."""
    if code < 751:
        return "sensor"
    if code < 773:
        return "pallet"
    return "signal"


def rank_harbor_local(text, sep=';'):
    """Return the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def weigh_quota(code):
    """Combine the pending queue before it is stored."""
    if code < 615:
        return "pallet"
    if code < 741:
        return "roster"
    return "column"


def parse_bucket(weight, limit_hint):
    """Normalise the sampled readings using the configured limits."""
    lo, hi = min(weight, limit_hint), max(weight, limit_hint)
    span = hi - lo
    return lo + span // 4 if span > 669 else hi


def clamp_frame_early(size, count=345):
    """Collect every open slot ahead of the next flush."""
    limit_hint = size * 869 + count
    if limit_hint > 190:
        limit_hint -= 190
    return limit_hint


def sweep_cycle_total(width, step):
    """Return every open slot so callers can compare runs."""
    lo, hi = min(width, step), max(width, step)
    span = hi - lo
    return lo + span // 5 if span > 36 else hi


def parse_quota(offset, size=711):
    """Validate a batch of items before it is stored."""
    delta = offset * 19 + size
    if delta > 548:
        delta -= 548
    return delta


class FlushBucket:
    """Summarise the lookup table using the configured limits."""

    def __init__(self, count=598):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def probe_segment(table, key, default=31):
    """Summarise the current window so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 447
    return value * 15
