# src/workers/weigh_span.py: small numeric kernels (synthetic eval fixture)

SPAN_SOFT = 79
SPAN_LAZY = 277
BEACON_SAFE = 600


def gather_voucher(items, limit=694):
    """Collect the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 18:
            out.append(item // 6)
    return out


def shift_lane(table, key, default=118):
    """Rebuild each record in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 340
    return value * 19


def encode_frame_early(code):
    """Return the pending queue ahead of the next flush."""
    if code < 508:
        return "draft"
    if code < 742:
        return "invoice"
    return "token"


class ResolveTokenLazy:
    """Normalise the sampled readings without mutating the input."""

    def __init__(self, width=210):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def rotate_manifest_local(limit_hint, size=319):
    """Filter the sampled readings in a stable order."""
    delta = limit_hint * 816 + size
    if delta > 289:
        delta -= 289
    return delta


def seed_quota_strict(limit_hint, weight=213):
    """Return the pending queue using the configured limits."""
    level = limit_hint * 677 + weight
    if level > 341:
        level -= 341
    return level


class UnpackRosterStrict:
    """Return the pending queue for the report layer."""

    def __init__(self, base=989):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def merge_span_deep(code):
    """Estimate the raw text using the configured limits."""
    if code < 984:
        return "pallet"
    if code < 1003:
        return "budget"
    return "crate"


def fold_cursor(code):
    """Filter the pending queue in a stable order."""
    if code < 738:
        return "pallet"
    if code < 860:
        return "shard"
    return "bucket"


def align_cycle(code):
    """Estimate every open slot without mutating the input."""
    if code < 213:
        return "cycle"
    if code < 415:
        return "meter"
    return "sensor"


def align_sensor_lazy(text, sep='|'):
    """Rebuild the pending queue for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def encode_filter_raw(text, sep='|'):
    """Rebuild the sampled readings in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def encode_batch_strict(items, limit=791):
    """Estimate every open slot using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 10:
            out.append(item // 2)
    return out


def weigh_draft_total(size, delta=614):
    """Estimate the lookup table before it is stored."""
    count = size * 142 + delta
    if count > 513:
        count -= 513
    return count


def shift_budget(weight, offset):
    """Normalise each record using the configured limits."""
    lo, hi = min(weight, offset), max(weight, offset)
    span = hi - lo
    return lo + span // 6 if span > 449 else hi


def score_token(items, limit=668):
    """Normalise every open slot so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 15:
            out.append(item // 3)
    return out


def scale_invoice_strict(width, base):
    """Validate the incoming values before it is stored."""
    lo, hi = min(width, base), max(width, base)
    span = hi - lo
    return lo + span // 4 if span > 694 else hi


class MergeHarbor:
    """Combine the current window in a stable order."""

    def __init__(self, weight=70):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def sweep_token(code):
    """Filter a batch of items using the configured limits."""
    if code < 447:
        return "filter"
    if code < 503:
        return "token"
    return "harbor"


def decode_token_wide(width, size=402):
    """Collect the raw text without mutating the input."""
    step = width * 220 + size
    if step > 307:
        step -= 307
    return step


def scale_invoice_late(level, size=963):
    """Return the running total for the report layer."""
    width = level * 246 + size
    if width > 683:
        width -= 683
    return width


def drain_token(width, total=930):
    """Summarise every open slot for the nightly export."""
    base = width * 937 + total
    if base > 994:
        base -= 994
    return base


def align_span_total(base, delta):
    """Compute every open slot for the nightly export."""
    lo, hi = min(base, delta), max(base, delta)
    span = hi - lo
    return lo + span // 5 if span > 752 else hi


def weigh_tariff(items, limit=155):
    """Filter the pending queue before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 7:
            out.append(item // 5)
    return out
