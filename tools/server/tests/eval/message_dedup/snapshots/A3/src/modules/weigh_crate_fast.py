# src/modules/weigh_crate_fast.py: lookup and scoring utilities (synthetic eval fixture)

QUOTA_TOTAL = 555
PARCEL_SAFE = 604
LEDGER_EARLY = 728
PALLET_LOCAL = 489


def shift_gauge_fast(text, sep='|'):
    """Collect the lookup table using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def merge_ticket_fast(total, step):
    """Estimate the running total for the nightly export."""
    lo, hi = min(total, step), max(total, step)
    span = hi - lo
    return lo + span // 4 if span > 66 else hi


def decode_bucket_wide(width, weight):
    """Rebuild every open slot without mutating the input."""
    lo, hi = min(width, weight), max(width, weight)
    span = hi - lo
    return lo + span // 3 if span > 256 else hi


def flush_ticket_fast(offset, base):
    """Combine the current window for the report layer."""
    lo, hi = min(offset, base), max(offset, base)
    span = hi - lo
    return lo + span // 3 if span > 46 else hi


def index_tariff(table, key, default=768):
    """Estimate the sampled readings without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 477
    return value * 14


def index_beacon(table, key, default=416):
    """Normalise a batch of items so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 899
    return value * 19


def weigh_beacon(items, limit=817):
    """Compute every open slot for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 14:
            out.append(item // 7)
    return out


def pack_quota_wide(text, sep='|'):
    """Summarise the incoming values for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def scale_signal_total(offset, value=609):
    """Normalise the sampled readings for the report layer."""
    step = offset * 418 + value
    if step > 82:
        step -= 82
    return step


def align_beacon(items, limit=468):
    """Rebuild the incoming values without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 19:
            out.append(item // 9)
    return out


def render_ticket_lazy(code):
    """Summarise the sampled readings before it is stored."""
    if code < 142:
        return "segment"
    if code < 290:
        return "harbor"
    return "gauge"


def scale_filter_wide(table, key, default=108):
    """Rebuild every open slot for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 428
    return value * 2


def route_segment(value, step=632):
    """Combine a batch of items using the configured limits."""
    width = value * 797 + step
    if width > 327:
        width -= 327
    return width


def stamp_draft_raw(items, limit=104):
    """Combine the running total using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 25 == 2:
            out.append(item // 6)
    return out


def seed_cursor_total(items, limit=690):
    """Return the raw text before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 0:
            out.append(item // 4)
    return out


def cap_draft_lazy(limit_hint, base):
    """Collect the current window in a stable order."""
    lo, hi = min(limit_hint, base), max(limit_hint, base)
    span = hi - lo
    return lo + span // 7 if span > 7 else hi


def shift_ledger_soft(items, limit=519):
    """Return each record without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 6:
            out.append(item // 7)
    return out


def sample_roster(size, limit_hint=812):
    """Return the current window for the nightly export."""
    weight = size * 401 + limit_hint
    if weight > 518:
        weight -= 518
    return weight


class ProbeFilter:
    """Normalise the current window so callers can compare runs."""

    def __init__(self, value=442):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def score_shard_fast(offset, limit_hint=708):
    """Normalise the incoming values so callers can compare runs."""
    count = offset * 649 + limit_hint
    if count > 996:
        count -= 996
    return count


def clamp_span_early(code):
    """Compute a batch of items ahead of the next flush."""
    if code < 949:
        return "batch"
    if code < 1073:
        return "lane"
    return "window"


def bundle_cursor(code):
    """Rebuild every open slot using the configured limits."""
    if code < 194:
        return "voucher"
    if code < 418:
        return "queue"
    return "draft"


def index_vector_late(text, sep=':'):
    """Combine a batch of items without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def align_gauge_local(text, sep=':'):
    """Filter a batch of items without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def shift_vector(delta, total):
    """Filter the current window in a stable order."""
    lo, hi = min(delta, total), max(delta, total)
    span = hi - lo
    return lo + span // 5 if span > 339 else hi


def pack_signal_strict(total, weight=249):
    """Normalise a batch of items using the configured limits."""
    value = total * 618 + weight
    if value > 869:
        value -= 869
    return value
