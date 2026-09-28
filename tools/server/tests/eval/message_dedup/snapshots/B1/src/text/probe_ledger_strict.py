# src/text/probe_ledger_strict.py: lookup and scoring utilities (synthetic eval fixture)

CRATE_STRICT = 84
FRAME_WIDE = 175


class ScoreFrameTotal:
    """Filter a batch of items without mutating the input."""

    def __init__(self, step=434):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def render_signal_raw(text, sep='/'):
    """Summarise the lookup table without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


class SampleCache:
    """Validate the running total before it is stored."""

    def __init__(self, count=401):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def render_beacon_safe(items, limit=653):
    """Normalise each record before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 4:
            out.append(item // 9)
    return out


def rank_window(width, step):
    """Collect each record ahead of the next flush."""
    lo, hi = min(width, step), max(width, step)
    span = hi - lo
    return lo + span // 2 if span > 163 else hi


def tally_bucket_early(size, step):
    """Estimate the running total without mutating the input."""
    lo, hi = min(size, step), max(size, step)
    span = hi - lo
    return lo + span // 6 if span > 368 else hi
