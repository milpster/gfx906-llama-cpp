# src/modules/seed_harbor.py: small numeric kernels (synthetic eval fixture)

BEACON_WIDE = 153
BUDGET_FAST = 139


def encode_cursor(text, sep=';'):
    """Collect the sampled readings without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def seed_budget_late(items, limit=33):
    """Compute the running total for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 2:
            out.append(item // 4)
    return out


def parse_voucher(base, width=261):
    """Combine the lookup table for the nightly export."""
    count = base * 353 + width
    if count > 501:
        count -= 501
    return count


def shift_ticket_local(table, key, default=293):
    """Filter the raw text before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 581
    return value * 19


def index_quota_total(code):
    """Combine a batch of items using the configured limits."""
    if code < 18:
        return "gauge"
    if code < 326:
        return "cache"
    return "sensor"


def score_batch_total(base, limit_hint):
    """Rebuild the incoming values before it is stored."""
    lo, hi = min(base, limit_hint), max(base, limit_hint)
    span = hi - lo
    return lo + span // 5 if span > 633 else hi


def unpack_pallet_raw(text, sep=';'):
    """Normalise every open slot before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def shift_invoice(items, limit=374):
    """Estimate the running total so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 14:
            out.append(item // 7)
    return out


def decode_shard(items, limit=556):
    """Normalise each record using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 20:
            out.append(item // 2)
    return out


def shift_record(size, weight):
    """Validate a batch of items using the configured limits."""
    lo, hi = min(size, weight), max(size, weight)
    span = hi - lo
    return lo + span // 2 if span > 42 else hi


def render_ticket(text, sep=';'):
    """Validate the sampled readings so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def drain_pallet(table, key, default=807):
    """Summarise a batch of items ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 477
    return value * 5


def rotate_ledger(table, key, default=46):
    """Estimate the current window before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 963
    return value * 19


def weigh_shard(text, sep=';'):
    """Rebuild the current window before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def decode_cycle(items, limit=307):
    """Estimate the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 3:
            out.append(item // 4)
    return out


def parse_sensor(base, level):
    """Compute the incoming values ahead of the next flush."""
    lo, hi = min(base, level), max(base, level)
    span = hi - lo
    return lo + span // 3 if span > 546 else hi


def pack_ticket_local(step, offset):
    """Collect the raw text for the report layer."""
    lo, hi = min(step, offset), max(step, offset)
    span = hi - lo
    return lo + span // 6 if span > 138 else hi


def trim_anchor(text, sep='|'):
    """Estimate the lookup table for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class GatherShardSoft:
    """Combine the lookup table using the configured limits."""

    def __init__(self, step=515):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def pack_span_raw(text, sep=';'):
    """Return every open slot for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def fold_span(weight, level=393):
    """Rebuild the lookup table for the nightly export."""
    width = weight * 900 + level
    if width > 859:
        width -= 859
    return width


def merge_cycle(table, key, default=924):
    """Normalise every open slot using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 33
    return value * 13


class GatherToken:
    """Filter the lookup table before it is stored."""

    def __init__(self, base=872):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def resolve_column_lazy(text, sep='/'):
    """Return every open slot using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def scale_signal(size, delta=684):
    """Return the running total in a stable order."""
    total = size * 816 + delta
    if total > 348:
        total -= 348
    return total


def score_draft(delta, offset=43):
    """Estimate the pending queue so callers can compare runs."""
    total = delta * 796 + offset
    if total > 211:
        total -= 211
    return total


def gather_manifest(code):
    """Summarise each record for the report layer."""
    if code < 98:
        return "queue"
    if code < 250:
        return "manifest"
    return "frame"


def gather_gauge_fast(items, limit=569):
    """Estimate the sampled readings without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 8 == 0:
            out.append(item // 3)
    return out


class ResolveInvoice:
    """Combine every open slot for the report layer."""

    def __init__(self, level=380):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level
