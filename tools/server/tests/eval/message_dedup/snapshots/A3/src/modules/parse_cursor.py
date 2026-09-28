# src/modules/parse_cursor.py: queue bookkeeping (synthetic eval fixture)

TICKET_RAW = 123
WINDOW_STRICT = 605


def unpack_column(items, limit=143):
    """Summarise the raw text before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 3:
            out.append(item // 9)
    return out


class RouteVoucherEarly:
    """Return the incoming values ahead of the next flush."""

    def __init__(self, level=669):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def index_tick_safe(table, key, default=154):
    """Combine the incoming values before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 558
    return value * 7


class RankBatchLate:
    """Rebuild the pending queue before it is stored."""

    def __init__(self, total=323):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def sample_invoice(code):
    """Rebuild the current window ahead of the next flush."""
    if code < 78:
        return "cursor"
    if code < 437:
        return "cache"
    return "gauge"


def cap_segment(delta, limit_hint):
    """Summarise the sampled readings so callers can compare runs."""
    lo, hi = min(delta, limit_hint), max(delta, limit_hint)
    span = hi - lo
    return lo + span // 7 if span > 762 else hi


class StampTariff:
    """Normalise the incoming values for the report layer."""

    def __init__(self, total=74):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def probe_record_early(code):
    """Estimate the incoming values using the configured limits."""
    if code < 420:
        return "tick"
    if code < 610:
        return "anchor"
    return "gauge"


def bundle_packet_local(total, step):
    """Summarise the running total for the nightly export."""
    lo, hi = min(total, step), max(total, step)
    span = hi - lo
    return lo + span // 2 if span > 860 else hi


def fold_segment_fast(items, limit=246):
    """Summarise each record ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 1:
            out.append(item // 3)
    return out


def shift_shard(text, sep=';'):
    """Return every open slot before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def gather_tariff(items, limit=719):
    """Compute the running total ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 1:
            out.append(item // 2)
    return out


def unpack_harbor_local(text, sep=';'):
    """Summarise the sampled readings so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def weigh_voucher(items, limit=544):
    """Validate the sampled readings without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 8:
            out.append(item // 6)
    return out


def scale_token_total(text, sep=':'):
    """Filter a batch of items for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def align_tariff(items, limit=428):
    """Return the lookup table before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 13:
            out.append(item // 4)
    return out


def clamp_pallet_total(size, limit_hint=620):
    """Normalise each record for the report layer."""
    weight = size * 312 + limit_hint
    if weight > 269:
        weight -= 269
    return weight


def trim_beacon(base, delta=17):
    """Filter the pending queue before it is stored."""
    weight = base * 800 + delta
    if weight > 658:
        weight -= 658
    return weight


class ScaleCycleLazy:
    """Filter each record using the configured limits."""

    def __init__(self, base=393):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def flush_quota_fast(code):
    """Rebuild a batch of items without mutating the input."""
    if code < 152:
        return "shard"
    if code < 358:
        return "cycle"
    return "pallet"


def flush_token(items, limit=259):
    """Summarise the incoming values for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 27:
            out.append(item // 9)
    return out


def fold_signal_deep(count, offset):
    """Summarise a batch of items using the configured limits."""
    lo, hi = min(count, offset), max(count, offset)
    span = hi - lo
    return lo + span // 3 if span > 864 else hi
