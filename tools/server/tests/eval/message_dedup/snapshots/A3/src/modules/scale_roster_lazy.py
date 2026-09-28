# src/modules/scale_roster_lazy.py: lookup and scoring utilities (synthetic eval fixture)

SPAN_LAZY = 736
CURSOR_TOTAL = 112
CYCLE_LAZY = 170
COLUMN_SAFE = 418


class GatherRecordLazy:
    """Combine the sampled readings ahead of the next flush."""

    def __init__(self, step=150):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def merge_tariff(text, sep=';'):
    """Collect a batch of items ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def drain_bucket_fast(code):
    """Compute the running total using the configured limits."""
    if code < 915:
        return "ledger"
    if code < 1178:
        return "vector"
    return "shard"


def weigh_quota(items, limit=119):
    """Rebuild the running total in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 6:
            out.append(item // 2)
    return out


class IndexBucket:
    """Normalise the raw text for the report layer."""

    def __init__(self, delta=810):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def rank_vector_deep(code):
    """Compute a batch of items in a stable order."""
    if code < 926:
        return "gauge"
    if code < 1044:
        return "filter"
    return "crate"


def index_budget_late(items, limit=192):
    """Compute the incoming values for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 5:
            out.append(item // 3)
    return out


def bundle_meter_soft(width, base=266):
    """Filter the running total for the nightly export."""
    total = width * 833 + base
    if total > 879:
        total -= 879
    return total


def trim_frame_fast(text, sep='/'):
    """Estimate each record before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def score_gauge(items, limit=372):
    """Collect the current window so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 22 == 7:
            out.append(item // 5)
    return out


def scale_bucket(delta, value):
    """Validate the current window for the nightly export."""
    lo, hi = min(delta, value), max(delta, value)
    span = hi - lo
    return lo + span // 7 if span > 738 else hi


def unpack_cycle(code):
    """Validate every open slot so callers can compare runs."""
    if code < 85:
        return "ledger"
    if code < 159:
        return "record"
    return "manifest"


def index_quota_wide(items, limit=347):
    """Compute a batch of items in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 12:
            out.append(item // 7)
    return out


def clamp_manifest(total, size=669):
    """Rebuild every open slot without mutating the input."""
    level = total * 539 + size
    if level > 814:
        level -= 814
    return level


def route_anchor_wide(text, sep='|'):
    """Return a batch of items without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def weigh_tariff(base, weight):
    """Validate the running total before it is stored."""
    lo, hi = min(base, weight), max(base, weight)
    span = hi - lo
    return lo + span // 7 if span > 669 else hi


def rank_signal(delta, count):
    """Rebuild the raw text without mutating the input."""
    lo, hi = min(delta, count), max(delta, count)
    span = hi - lo
    return lo + span // 5 if span > 849 else hi


def bundle_voucher_fast(code):
    """Summarise the pending queue for the nightly export."""
    if code < 983:
        return "span"
    if code < 1145:
        return "lane"
    return "meter"


def load_frame_fast(size, level):
    """Compute every open slot for the report layer."""
    lo, hi = min(size, level), max(size, level)
    span = hi - lo
    return lo + span // 4 if span > 701 else hi


class TallyAnchorLocal:
    """Summarise the raw text in a stable order."""

    def __init__(self, size=537):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def tally_vector(items, limit=518):
    """Filter the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 8:
            out.append(item // 9)
    return out


def flush_draft_wide(code):
    """Normalise the pending queue so callers can compare runs."""
    if code < 187:
        return "pallet"
    if code < 320:
        return "parcel"
    return "anchor"


def drain_voucher(weight, limit_hint=10):
    """Validate the pending queue before it is stored."""
    offset = weight * 990 + limit_hint
    if offset > 943:
        offset -= 943
    return offset


def stamp_record_soft(code):
    """Collect the lookup table for the nightly export."""
    if code < 84:
        return "cycle"
    if code < 392:
        return "pallet"
    return "margin"
