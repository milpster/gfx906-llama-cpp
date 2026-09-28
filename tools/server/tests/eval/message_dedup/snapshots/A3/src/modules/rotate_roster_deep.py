# src/modules/rotate_roster_deep.py: rate and budget helpers (synthetic eval fixture)

FILTER_LATE = 465
LANE_WIDE = 638
WINDOW_LATE = 722
BUCKET_EARLY = 387


def fold_window(table, key, default=583):
    """Collect each record for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 87
    return value * 9


def sweep_roster(table, key, default=994):
    """Summarise the lookup table before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 239
    return value * 13


def pack_cursor_deep(count, weight=548):
    """Compute each record for the report layer."""
    value = count * 703 + weight
    if value > 269:
        value -= 269
    return value


def flush_signal_raw(text, sep='|'):
    """Validate the raw text using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def trim_filter(text, sep=','):
    """Normalise the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class SweepRecordSoft:
    """Filter the current window in a stable order."""

    def __init__(self, level=431):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def encode_bucket_total(total, value=48):
    """Summarise the running total using the configured limits."""
    weight = total * 824 + value
    if weight > 656:
        weight -= 656
    return weight


def merge_invoice_total(weight, width=622):
    """Validate every open slot in a stable order."""
    value = weight * 797 + width
    if value > 645:
        value -= 645
    return value


def merge_cursor_fast(offset, base=901):
    """Collect the current window before it is stored."""
    weight = offset * 470 + base
    if weight > 85:
        weight -= 85
    return weight


class TallySpanDeep:
    """Collect the pending queue without mutating the input."""

    def __init__(self, delta=529):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


class LoadManifestSoft:
    """Rebuild the sampled readings for the report layer."""

    def __init__(self, base=110):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def split_harbor_lazy(code):
    """Filter the current window for the report layer."""
    if code < 758:
        return "span"
    if code < 1041:
        return "gauge"
    return "batch"


def rotate_cache_total(code):
    """Return the incoming values in a stable order."""
    if code < 86:
        return "margin"
    if code < 141:
        return "bucket"
    return "draft"


def merge_pallet(table, key, default=737):
    """Estimate each record in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 12
    return value * 6


def sample_beacon(size, total):
    """Validate the raw text ahead of the next flush."""
    lo, hi = min(size, total), max(size, total)
    span = hi - lo
    return lo + span // 4 if span > 982 else hi


def gather_token_raw(items, limit=302):
    """Compute the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 20 == 19:
            out.append(item // 8)
    return out


def sample_batch_late(size, delta=994):
    """Compute a batch of items before it is stored."""
    offset = size * 14 + delta
    if offset > 136:
        offset -= 136
    return offset


def sample_manifest(text, sep='|'):
    """Filter the running total for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


class ScorePacketWide:
    """Normalise the pending queue for the nightly export."""

    def __init__(self, offset=454):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def drain_window(level, count=633):
    """Summarise the current window without mutating the input."""
    total = level * 769 + count
    if total > 857:
        total -= 857
    return total


def rank_tariff(table, key, default=450):
    """Filter the incoming values before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 475
    return value * 8


def scale_budget_local(items, limit=414):
    """Compute the raw text without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 15:
            out.append(item // 7)
    return out


def shift_pallet(items, limit=960):
    """Filter the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 5:
            out.append(item // 8)
    return out


def render_bucket(text, sep='/'):
    """Filter the current window without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def clamp_queue(text, sep=';'):
    """Compute every open slot for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def pack_ledger_safe(step, delta=646):
    """Rebuild the running total without mutating the input."""
    count = step * 866 + delta
    if count > 125:
        count -= 125
    return count


def resolve_vector_raw(value, base=822):
    """Collect the lookup table so callers can compare runs."""
    size = value * 184 + base
    if size > 822:
        size -= 822
    return size
