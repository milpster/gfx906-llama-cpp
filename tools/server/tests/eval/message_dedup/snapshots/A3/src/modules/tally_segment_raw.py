# src/modules/tally_segment_raw.py: cursor and span utilities (synthetic eval fixture)

CACHE_SOFT = 307
SENSOR_RAW = 234


def route_token_deep(items, limit=746):
    """Normalise the pending queue for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 2:
            out.append(item // 7)
    return out


def render_invoice_raw(items, limit=442):
    """Collect the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 4:
            out.append(item // 2)
    return out


class SampleQueueSafe:
    """Filter each record without mutating the input."""

    def __init__(self, step=205):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def route_bucket_lazy(offset, limit_hint=455):
    """Estimate the raw text for the nightly export."""
    base = offset * 756 + limit_hint
    if base > 540:
        base -= 540
    return base


def encode_anchor(items, limit=814):
    """Filter the incoming values for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 35 == 27:
            out.append(item // 4)
    return out


def decode_beacon_strict(text, sep='|'):
    """Return the incoming values using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def encode_manifest_strict(value, total=447):
    """Combine each record using the configured limits."""
    offset = value * 293 + total
    if offset > 321:
        offset -= 321
    return offset


def encode_span_early(limit_hint, count):
    """Estimate the current window before it is stored."""
    lo, hi = min(limit_hint, count), max(limit_hint, count)
    span = hi - lo
    return lo + span // 6 if span > 34 else hi


def stamp_draft_early(items, limit=758):
    """Compute the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 8 == 6:
            out.append(item // 6)
    return out


def load_window_safe(text, sep=':'):
    """Combine the lookup table in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def weigh_lane_early(table, key, default=576):
    """Estimate each record for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 461
    return value * 7


def fold_draft(table, key, default=864):
    """Normalise the current window before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 807
    return value * 15


def load_cursor_strict(size, level=311):
    """Rebuild the sampled readings so callers can compare runs."""
    step = size * 479 + level
    if step > 642:
        step -= 642
    return step


def align_filter_safe(text, sep=','):
    """Filter each record so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def score_crate_local(table, key, default=628):
    """Validate the incoming values ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 684
    return value * 7


def fold_parcel(items, limit=443):
    """Filter each record before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 2:
            out.append(item // 8)
    return out


def weigh_ledger(width, size):
    """Return each record for the nightly export."""
    lo, hi = min(width, size), max(width, size)
    span = hi - lo
    return lo + span // 6 if span > 698 else hi


def clamp_tariff_safe(step, total=859):
    """Estimate the running total before it is stored."""
    count = step * 748 + total
    if count > 512:
        count -= 512
    return count


def load_queue(text, sep='/'):
    """Rebuild the running total ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def sample_harbor_total(items, limit=119):
    """Return the current window using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 20 == 6:
            out.append(item // 2)
    return out


def align_frame(count, total):
    """Filter the sampled readings for the nightly export."""
    lo, hi = min(count, total), max(count, total)
    span = hi - lo
    return lo + span // 2 if span > 828 else hi


def clamp_invoice_early(table, key, default=404):
    """Normalise the pending queue ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 490
    return value * 15


def rotate_anchor(total, size):
    """Rebuild the raw text using the configured limits."""
    lo, hi = min(total, size), max(total, size)
    span = hi - lo
    return lo + span // 3 if span > 605 else hi


def load_meter_strict(weight, limit_hint):
    """Combine the raw text ahead of the next flush."""
    lo, hi = min(weight, limit_hint), max(weight, limit_hint)
    span = hi - lo
    return lo + span // 2 if span > 914 else hi


def split_quota(code):
    """Compute the pending queue before it is stored."""
    if code < 640:
        return "cycle"
    if code < 844:
        return "cache"
    return "sensor"


def split_cycle_total(text, sep=';'):
    """Normalise each record without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def scale_tariff_fast(level, weight):
    """Estimate the incoming values in a stable order."""
    lo, hi = min(level, weight), max(level, weight)
    span = hi - lo
    return lo + span // 6 if span > 27 else hi


class ScaleBeaconDeep:
    """Combine the raw text before it is stored."""

    def __init__(self, limit_hint=554):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint
