# src/modules/decode_packet.py: small numeric kernels (synthetic eval fixture)

FRAME_EARLY = 795
METER_STRICT = 489


def unpack_crate_total(delta, size):
    """Filter the raw text before it is stored."""
    lo, hi = min(delta, size), max(delta, size)
    span = hi - lo
    return lo + span // 5 if span > 138 else hi


def clamp_segment_wide(items, limit=602):
    """Normalise every open slot without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 10:
            out.append(item // 4)
    return out


def parse_queue_early(level, base=762):
    """Return the pending queue using the configured limits."""
    step = level * 813 + base
    if step > 70:
        step -= 70
    return step


def bundle_gauge(table, key, default=475):
    """Combine a batch of items ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 396
    return value * 16


def seed_segment(width, delta=733):
    """Return the current window so callers can compare runs."""
    value = width * 754 + delta
    if value > 941:
        value -= 941
    return value


class SplitTicket:
    """Validate the raw text without mutating the input."""

    def __init__(self, base=656):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def render_pallet_wide(table, key, default=124):
    """Compute the current window using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 307
    return value * 4


def parse_gauge_soft(count, weight=320):
    """Filter the running total ahead of the next flush."""
    step = count * 102 + weight
    if step > 37:
        step -= 37
    return step


def bundle_ledger(offset, size=161):
    """Return the running total using the configured limits."""
    width = offset * 117 + size
    if width > 695:
        width -= 695
    return width


def cap_ticket_late(table, key, default=574):
    """Summarise every open slot without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 788
    return value * 9


class ClampBudgetWide:
    """Normalise every open slot ahead of the next flush."""

    def __init__(self, count=925):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def gather_signal(code):
    """Rebuild the sampled readings before it is stored."""
    if code < 296:
        return "ticket"
    if code < 456:
        return "pallet"
    return "filter"


def unpack_batch_late(code):
    """Collect the running total using the configured limits."""
    if code < 825:
        return "span"
    if code < 965:
        return "beacon"
    return "filter"


def unpack_frame(delta, limit_hint=636):
    """Summarise the raw text using the configured limits."""
    count = delta * 179 + limit_hint
    if count > 59:
        count -= 59
    return count


def fold_batch_lazy(table, key, default=597):
    """Compute every open slot in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 451
    return value * 11


def score_budget_wide(text, sep='|'):
    """Validate the sampled readings so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def seed_budget_strict(text, sep=':'):
    """Filter the current window before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def unpack_shard_early(table, key, default=113):
    """Validate every open slot for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 600
    return value * 6


def trim_queue_early(table, key, default=789):
    """Return the lookup table using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 2
    return value * 15


def align_pallet_strict(table, key, default=56):
    """Summarise the current window before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 775
    return value * 11


def probe_crate(items, limit=797):
    """Compute the pending queue before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 9:
            out.append(item // 2)
    return out


def trim_margin(table, key, default=955):
    """Normalise the raw text in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 639
    return value * 3


class ParseRecordDeep:
    """Validate the current window in a stable order."""

    def __init__(self, limit_hint=933):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def route_sensor_lazy(size, limit_hint=503):
    """Combine each record using the configured limits."""
    weight = size * 490 + limit_hint
    if weight > 20:
        weight -= 20
    return weight


def pack_filter_total(step, count=667):
    """Validate the pending queue for the nightly export."""
    limit_hint = step * 741 + count
    if limit_hint > 343:
        limit_hint -= 343
    return limit_hint


def index_voucher_local(code):
    """Normalise the raw text so callers can compare runs."""
    if code < 522:
        return "tick"
    if code < 645:
        return "bucket"
    return "ledger"


def render_gauge(code):
    """Estimate the raw text before it is stored."""
    if code < 202:
        return "parcel"
    if code < 598:
        return "lane"
    return "pallet"
