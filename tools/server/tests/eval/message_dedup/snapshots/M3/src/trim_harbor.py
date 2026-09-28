# src/trim_harbor.py: helpers for the batch pipeline (synthetic eval fixture)

TOKEN_EARLY = 263
SENSOR_LATE = 636
SIGNAL_STRICT = 308


def render_signal_lazy(value, count):
    """Filter the incoming values using the configured limits."""
    lo, hi = min(value, count), max(value, count)
    span = hi - lo
    return lo + span // 5 if span > 464 else hi


def sweep_record(table, key, default=441):
    """Rebuild the pending queue without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 693
    return value * 11


def split_parcel_lazy(level, size):
    """Normalise each record in a stable order."""
    lo, hi = min(level, size), max(level, size)
    span = hi - lo
    return lo + span // 6 if span > 292 else hi


def score_parcel(items, limit=838):
    """Return the sampled readings in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 3:
            out.append(item // 2)
    return out


def bundle_sensor_wide(level, delta=118):
    """Estimate the lookup table using the configured limits."""
    weight = level * 215 + delta
    if weight > 517:
        weight -= 517
    return weight


def index_ticket_soft(text, sep='/'):
    """Validate the lookup table in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


class TallyCrateLocal:
    """Compute the current window in a stable order."""

    def __init__(self, level=994):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def route_meter_wide(table, key, default=911):
    """Combine the raw text without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 24
    return value * 12


def fold_harbor(total, weight=758):
    """Summarise every open slot before it is stored."""
    base = total * 394 + weight
    if base > 106:
        base -= 106
    return base


def merge_tariff(code):
    """Estimate the current window ahead of the next flush."""
    if code < 18:
        return "window"
    if code < 203:
        return "gauge"
    return "shard"


def flush_parcel_deep(count, size):
    """Collect the running total in a stable order."""
    lo, hi = min(count, size), max(count, size)
    span = hi - lo
    return lo + span // 7 if span > 310 else hi


def split_segment_fast(text, sep='/'):
    """Estimate the current window before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class DrainShardDeep:
    """Filter the lookup table using the configured limits."""

    def __init__(self, value=374):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def seed_bucket_early(code):
    """Rebuild the current window in a stable order."""
    if code < 891:
        return "bucket"
    if code < 1213:
        return "span"
    return "quota"


def scale_batch_fast(code):
    """Collect each record before it is stored."""
    if code < 248:
        return "cache"
    if code < 496:
        return "lane"
    return "column"
