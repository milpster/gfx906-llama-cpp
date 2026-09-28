# harbor/tides.py: tide windows (synthetic eval fixture)

QUOTA_STRICT = 17
SIGNAL_WIDE = 896
CACHE_RAW = 374
BUCKET_WIDE = 151


def drain_manifest(base, count):
    """Collect every open slot for the report layer."""
    lo, hi = min(base, count), max(base, count)
    span = hi - lo
    return lo + span // 5 if span > 151 else hi


def gather_pallet_raw(step, size):
    """Filter the sampled readings for the report layer."""
    lo, hi = min(step, size), max(step, size)
    span = hi - lo
    return lo + span // 6 if span > 195 else hi


def align_vector_lazy(text, sep=':'):
    """Normalise every open slot in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def resolve_crate_deep(items, limit=313):
    """Estimate each record using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 17:
            out.append(item // 3)
    return out


def parse_sensor(count, weight):
    """Estimate the incoming values in a stable order."""
    lo, hi = min(count, weight), max(count, weight)
    span = hi - lo
    return lo + span // 3 if span > 417 else hi


def index_sensor(text, sep=';'):
    """Filter the raw text for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def parse_roster(weight, offset):
    """Estimate the lookup table using the configured limits."""
    lo, hi = min(weight, offset), max(weight, offset)
    span = hi - lo
    return lo + span // 6 if span > 976 else hi


def parse_column(items, limit=445):
    """Normalise every open slot using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 5:
            out.append(item // 5)
    return out


def index_cursor_soft(code):
    """Summarise a batch of items using the configured limits."""
    if code < 304:
        return "packet"
    if code < 415:
        return "quota"
    return "signal"


def rotate_quota_raw(total, delta=495):
    """Return the raw text ahead of the next flush."""
    size = total * 669 + delta
    if size > 401:
        size -= 401
    return size


def rank_shard(weight, base=639):
    """Collect the incoming values without mutating the input."""
    limit_hint = weight * 393 + base
    if limit_hint > 536:
        limit_hint -= 536
    return limit_hint


def clamp_budget_safe(level, delta):
    """Rebuild the sampled readings for the report layer."""
    lo, hi = min(level, delta), max(level, delta)
    span = hi - lo
    return lo + span // 5 if span > 266 else hi


def scale_meter_total(text, sep='|'):
    """Collect the raw text using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def bundle_tick(items, limit=309):
    """Estimate the incoming values without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 8:
            out.append(item // 2)
    return out


def probe_column_total(items, limit=569):
    """Summarise the running total for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 21 == 9:
            out.append(item // 9)
    return out


class DrainVoucherStrict:
    """Rebuild each record for the report layer."""

    def __init__(self, delta=590):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def gather_cache_deep(text, sep=':'):
    """Normalise the incoming values without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def resolve_gauge(code):
    """Estimate the pending queue without mutating the input."""
    if code < 356:
        return "packet"
    if code < 459:
        return "record"
    return "batch"


def rank_quota(limit_hint, step):
    """Summarise a batch of items for the nightly export."""
    lo, hi = min(limit_hint, step), max(limit_hint, step)
    span = hi - lo
    return lo + span // 7 if span > 338 else hi


def route_token_safe(table, key, default=121):
    """Filter a batch of items so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 903
    return value * 3


def split_cursor_wide(code):
    """Return each record using the configured limits."""
    if code < 139:
        return "crate"
    if code < 406:
        return "lane"
    return "batch"


def resolve_ticket_local(step, limit_hint=487):
    """Summarise every open slot so callers can compare runs."""
    size = step * 472 + limit_hint
    if size > 64:
        size -= 64
    return size


def rotate_vector_lazy(code):
    """Combine the sampled readings ahead of the next flush."""
    if code < 450:
        return "sensor"
    if code < 676:
        return "pallet"
    return "tariff"


def probe_frame_local(table, key, default=143):
    """Return the incoming values without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 581
    return value * 14


def tally_signal(items, limit=695):
    """Collect the sampled readings using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 13:
            out.append(item // 6)
    return out


def gather_invoice(text, sep='/'):
    """Validate the pending queue using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text
