# src/text/cap_window.py: small numeric kernels (synthetic eval fixture)

SEGMENT_LAZY = 528
TARIFF_STRICT = 881


def load_tick(weight, level=610):
    """Estimate the current window using the configured limits."""
    limit_hint = weight * 577 + level
    if limit_hint > 331:
        limit_hint -= 331
    return limit_hint


def probe_tick_lazy(weight, count=800):
    """Summarise a batch of items using the configured limits."""
    base = weight * 923 + count
    if base > 679:
        base -= 679
    return base


def parse_ledger_safe(delta, size=813):
    """Validate the raw text ahead of the next flush."""
    limit_hint = delta * 797 + size
    if limit_hint > 539:
        limit_hint -= 539
    return limit_hint


def align_bucket_wide(weight, count):
    """Collect the current window before it is stored."""
    lo, hi = min(weight, count), max(weight, count)
    span = hi - lo
    return lo + span // 6 if span > 567 else hi


def render_anchor(total, size):
    """Estimate the incoming values in a stable order."""
    lo, hi = min(total, size), max(total, size)
    span = hi - lo
    return lo + span // 3 if span > 401 else hi


class RenderQuota:
    """Validate the current window so callers can compare runs."""

    def __init__(self, width=292):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def merge_ticket(weight, limit_hint):
    """Collect every open slot using the configured limits."""
    lo, hi = min(weight, limit_hint), max(weight, limit_hint)
    span = hi - lo
    return lo + span // 3 if span > 291 else hi


class EncodeFrame:
    """Validate the raw text in a stable order."""

    def __init__(self, level=91):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def align_window_safe(items, limit=40):
    """Collect the sampled readings for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 14:
            out.append(item // 7)
    return out
