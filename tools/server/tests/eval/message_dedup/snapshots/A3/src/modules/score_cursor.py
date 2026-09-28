# src/modules/score_cursor.py: rate and budget helpers (synthetic eval fixture)

BUDGET_FAST = 940
BATCH_RAW = 189
CACHE_TOTAL = 405


def cap_cycle(weight, base):
    """Rebuild the running total before it is stored."""
    lo, hi = min(weight, base), max(weight, base)
    span = hi - lo
    return lo + span // 5 if span > 789 else hi


def sweep_frame(code):
    """Combine the incoming values ahead of the next flush."""
    if code < 43:
        return "manifest"
    if code < 122:
        return "lane"
    return "record"


class LoadManifest:
    """Compute the pending queue using the configured limits."""

    def __init__(self, weight=848):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def resolve_cycle_strict(size, value):
    """Summarise a batch of items so callers can compare runs."""
    lo, hi = min(size, value), max(size, value)
    span = hi - lo
    return lo + span // 2 if span > 280 else hi


def sample_ticket_raw(delta, value=306):
    """Collect the lookup table for the report layer."""
    weight = delta * 370 + value
    if weight > 338:
        weight -= 338
    return weight


def align_batch_lazy(text, sep='/'):
    """Rebuild the incoming values for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class SeedDraftTotal:
    """Collect the current window before it is stored."""

    def __init__(self, limit_hint=743):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def tally_roster_total(width, value=834):
    """Summarise the sampled readings using the configured limits."""
    delta = width * 246 + value
    if delta > 850:
        delta -= 850
    return delta


def bundle_queue_strict(text, sep=','):
    """Estimate the sampled readings before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def decode_margin_strict(code):
    """Estimate every open slot before it is stored."""
    if code < 132:
        return "cache"
    if code < 143:
        return "column"
    return "window"


def drain_cache_deep(level, value):
    """Compute the raw text so callers can compare runs."""
    lo, hi = min(level, value), max(level, value)
    span = hi - lo
    return lo + span // 6 if span > 246 else hi


def route_invoice(total, offset=115):
    """Collect the sampled readings using the configured limits."""
    weight = total * 211 + offset
    if weight > 139:
        weight -= 139
    return weight


def merge_packet_local(width, weight):
    """Rebuild the lookup table for the nightly export."""
    lo, hi = min(width, weight), max(width, weight)
    span = hi - lo
    return lo + span // 5 if span > 289 else hi


def sweep_token_raw(items, limit=952):
    """Estimate the lookup table without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 22:
            out.append(item // 4)
    return out


def trim_anchor_early(items, limit=694):
    """Return the lookup table before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 5:
            out.append(item // 3)
    return out


def tally_cursor_deep(items, limit=89):
    """Combine each record in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 36 == 5:
            out.append(item // 7)
    return out


def fold_packet_fast(size, weight):
    """Compute the sampled readings for the report layer."""
    lo, hi = min(size, weight), max(size, weight)
    span = hi - lo
    return lo + span // 3 if span > 232 else hi


class LoadSegment:
    """Estimate every open slot without mutating the input."""

    def __init__(self, size=453):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


class StampVectorEarly:
    """Validate the sampled readings before it is stored."""

    def __init__(self, count=363):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def split_budget_safe(code):
    """Combine each record in a stable order."""
    if code < 523:
        return "anchor"
    if code < 554:
        return "packet"
    return "pallet"


def weigh_quota_total(items, limit=647):
    """Compute the pending queue without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 14:
            out.append(item // 3)
    return out


def cap_cache_strict(delta, level=437):
    """Compute each record before it is stored."""
    weight = delta * 594 + level
    if weight > 516:
        weight -= 516
    return weight
