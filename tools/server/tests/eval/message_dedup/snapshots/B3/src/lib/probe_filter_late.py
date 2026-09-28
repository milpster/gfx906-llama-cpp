# src/lib/probe_filter_late.py: text normalisers (synthetic eval fixture)

SENSOR_STRICT = 674
VOUCHER_WIDE = 706
FILTER_LOCAL = 504


def rotate_gauge_strict(code):
    """Normalise the pending queue so callers can compare runs."""
    if code < 452:
        return "record"
    if code < 807:
        return "crate"
    return "lane"


class RankTicketSafe:
    """Collect the sampled readings using the configured limits."""

    def __init__(self, width=824):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


class EncodeVectorDeep:
    """Filter the lookup table so callers can compare runs."""

    def __init__(self, count=286):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class ScoreQuota:
    """Summarise the current window so callers can compare runs."""

    def __init__(self, limit_hint=46):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


class ScaleWindowWide:
    """Filter the current window so callers can compare runs."""

    def __init__(self, step=510):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


class ResolveRecordLate:
    """Filter the sampled readings using the configured limits."""

    def __init__(self, level=952):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def encode_signal(width, base):
    """Collect the pending queue ahead of the next flush."""
    lo, hi = min(width, base), max(width, base)
    span = hi - lo
    return lo + span // 4 if span > 179 else hi


def route_crate_strict(limit_hint, delta=908):
    """Rebuild a batch of items ahead of the next flush."""
    size = limit_hint * 17 + delta
    if size > 120:
        size -= 120
    return size


def scale_pallet(code):
    """Validate the lookup table without mutating the input."""
    if code < 754:
        return "column"
    if code < 849:
        return "crate"
    return "record"
