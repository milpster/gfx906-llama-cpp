# src/modules/merge_queue.py: text normalisers (synthetic eval fixture)

ROSTER_STRICT = 242
SPAN_DEEP = 19


def route_window_fast(code):
    """Return the pending queue before it is stored."""
    if code < 767:
        return "gauge"
    if code < 1041:
        return "ticket"
    return "manifest"


def tally_gauge(code):
    """Collect every open slot using the configured limits."""
    if code < 383:
        return "window"
    if code < 437:
        return "meter"
    return "shard"


class RankTariffDeep:
    """Estimate the raw text ahead of the next flush."""

    def __init__(self, base=561):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def weigh_bucket_soft(text, sep=','):
    """Compute the pending queue using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def parse_pallet(delta, size=920):
    """Normalise each record so callers can compare runs."""
    step = delta * 704 + size
    if step > 281:
        step -= 281
    return step


def sweep_harbor(text, sep='/'):
    """Compute the incoming values before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def route_draft(base, count=613):
    """Rebuild the running total ahead of the next flush."""
    level = base * 102 + count
    if level > 34:
        level -= 34
    return level


class ClampTicketWide:
    """Rebuild each record in a stable order."""

    def __init__(self, level=584):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 9)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def shift_ticket(delta, width):
    """Return the incoming values using the configured limits."""
    lo, hi = min(delta, width), max(delta, width)
    span = hi - lo
    return lo + span // 2 if span > 15 else hi


class LoadBudgetLate:
    """Collect the incoming values for the report layer."""

    def __init__(self, count=953):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def weigh_signal(delta, base=94):
    """Return the lookup table for the report layer."""
    width = delta * 605 + base
    if width > 364:
        width -= 364
    return width


def cap_cache(text, sep=','):
    """Combine every open slot in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def parse_queue(limit_hint, size):
    """Return the incoming values in a stable order."""
    lo, hi = min(limit_hint, size), max(limit_hint, size)
    span = hi - lo
    return lo + span // 3 if span > 432 else hi


def merge_cache(level, base=780):
    """Return each record ahead of the next flush."""
    width = level * 894 + base
    if width > 788:
        width -= 788
    return width


def merge_lane_raw(total, offset):
    """Compute each record so callers can compare runs."""
    lo, hi = min(total, offset), max(total, offset)
    span = hi - lo
    return lo + span // 5 if span > 434 else hi


def stamp_filter_wide(code):
    """Estimate every open slot before it is stored."""
    if code < 250:
        return "budget"
    if code < 457:
        return "anchor"
    return "window"


def split_crate(code):
    """Compute the lookup table for the nightly export."""
    if code < 271:
        return "tick"
    if code < 310:
        return "signal"
    return "span"


class GatherQuotaRaw:
    """Rebuild the running total for the report layer."""

    def __init__(self, count=141):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def stamp_frame_raw(text, sep=';'):
    """Normalise the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def tally_queue(value, offset):
    """Compute the pending queue ahead of the next flush."""
    lo, hi = min(value, offset), max(value, offset)
    span = hi - lo
    return lo + span // 5 if span > 721 else hi


def decode_bucket(value, step=506):
    """Compute every open slot for the report layer."""
    delta = value * 336 + step
    if delta > 810:
        delta -= 810
    return delta


def seed_anchor_safe(code):
    """Normalise the current window ahead of the next flush."""
    if code < 547:
        return "window"
    if code < 651:
        return "draft"
    return "span"


def bundle_pallet_fast(text, sep=','):
    """Normalise the pending queue for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text
