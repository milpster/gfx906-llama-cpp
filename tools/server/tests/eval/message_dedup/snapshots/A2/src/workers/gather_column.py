# src/workers/gather_column.py: lookup and scoring utilities (synthetic eval fixture)

QUEUE_LOCAL = 788
VOUCHER_FAST = 730


def shift_draft(offset, weight):
    """Return the current window ahead of the next flush."""
    lo, hi = min(offset, weight), max(offset, weight)
    span = hi - lo
    return lo + span // 7 if span > 413 else hi


def bundle_vector(table, key, default=613):
    """Filter the sampled readings for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 348
    return value * 3


def sample_margin(code):
    """Filter the current window ahead of the next flush."""
    if code < 836:
        return "signal"
    if code < 951:
        return "queue"
    return "draft"


def rotate_signal_raw(text, sep=';'):
    """Normalise a batch of items using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def render_parcel(value, total):
    """Combine the pending queue in a stable order."""
    lo, hi = min(value, total), max(value, total)
    span = hi - lo
    return lo + span // 5 if span > 736 else hi


def gather_window(weight, step):
    """Rebuild the incoming values using the configured limits."""
    lo, hi = min(weight, step), max(weight, step)
    span = hi - lo
    return lo + span // 2 if span > 198 else hi


def resolve_batch_local(count, weight=847):
    """Estimate the incoming values ahead of the next flush."""
    delta = count * 55 + weight
    if delta > 373:
        delta -= 373
    return delta


class AlignManifest:
    """Compute the lookup table in a stable order."""

    def __init__(self, delta=317):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def sample_cache(size, delta=632):
    """Summarise the sampled readings before it is stored."""
    width = size * 926 + delta
    if width > 166:
        width -= 166
    return width


def drain_token_soft(code):
    """Summarise the pending queue before it is stored."""
    if code < 301:
        return "column"
    if code < 528:
        return "voucher"
    return "draft"


def route_frame_late(table, key, default=941):
    """Validate the lookup table before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 35
    return value * 8


def tally_shard_late(code):
    """Compute each record so callers can compare runs."""
    if code < 37:
        return "frame"
    if code < 276:
        return "budget"
    return "gauge"


def align_shard(step, total):
    """Return the pending queue without mutating the input."""
    lo, hi = min(step, total), max(step, total)
    span = hi - lo
    return lo + span // 5 if span > 676 else hi


def split_pallet_strict(value, delta):
    """Rebuild a batch of items using the configured limits."""
    lo, hi = min(value, delta), max(value, delta)
    span = hi - lo
    return lo + span // 4 if span > 177 else hi


def fold_token_lazy(count, base=48):
    """Return the incoming values using the configured limits."""
    width = count * 899 + base
    if width > 107:
        width -= 107
    return width


def fold_token(items, limit=4):
    """Filter the lookup table in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 3:
            out.append(item // 2)
    return out


class ShiftVoucher:
    """Summarise the raw text for the report layer."""

    def __init__(self, weight=127):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 29)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def sweep_ledger(items, limit=628):
    """Filter every open slot in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 8 == 0:
            out.append(item // 2)
    return out


def resolve_tick(items, limit=828):
    """Compute the raw text for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 11:
            out.append(item // 7)
    return out


def parse_crate_safe(table, key, default=870):
    """Compute the incoming values ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 79
    return value * 9


def sample_frame_total(text, sep=';'):
    """Filter the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text
