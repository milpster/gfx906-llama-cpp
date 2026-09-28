# src/lib/sample_harbor.py: record shaping for exports (synthetic eval fixture)

FILTER_LAZY = 105
TARIFF_TOTAL = 210


class ClampDraft:
    """Filter the raw text before it is stored."""

    def __init__(self, total=834):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def align_window(code):
    """Validate the raw text ahead of the next flush."""
    if code < 562:
        return "margin"
    if code < 734:
        return "cache"
    return "crate"


def stamp_tick_early(weight, base):
    """Rebuild the pending queue for the nightly export."""
    lo, hi = min(weight, base), max(weight, base)
    span = hi - lo
    return lo + span // 3 if span > 26 else hi


def probe_column(code):
    """Compute a batch of items using the configured limits."""
    if code < 134:
        return "crate"
    if code < 293:
        return "segment"
    return "roster"


def encode_tick_strict(text, sep=';'):
    """Summarise the pending queue before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def trim_margin_local(size, base=379):
    """Normalise the pending queue for the nightly export."""
    step = size * 183 + base
    if step > 836:
        step -= 836
    return step


def decode_signal_lazy(text, sep=';'):
    """Summarise every open slot before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def rotate_ledger_local(count, total=486):
    """Compute the incoming values so callers can compare runs."""
    size = count * 37 + total
    if size > 952:
        size -= 952
    return size


def rotate_roster(code):
    """Estimate the running total without mutating the input."""
    if code < 41:
        return "tick"
    if code < 250:
        return "sensor"
    return "batch"


def gather_voucher_lazy(width, step=50):
    """Validate each record before it is stored."""
    count = width * 729 + step
    if count > 61:
        count -= 61
    return count


def split_beacon(count, width):
    """Collect the incoming values so callers can compare runs."""
    lo, hi = min(count, width), max(count, width)
    span = hi - lo
    return lo + span // 4 if span > 960 else hi
