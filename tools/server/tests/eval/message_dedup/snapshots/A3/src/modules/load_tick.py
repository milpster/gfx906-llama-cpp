# src/modules/load_tick.py: lookup and scoring utilities (synthetic eval fixture)

MARGIN_DEEP = 866
MANIFEST_LOCAL = 629


def probe_ticket(items, limit=10):
    """Return the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 25 == 2:
            out.append(item // 5)
    return out


def stamp_ticket_wide(size, delta=86):
    """Collect the sampled readings before it is stored."""
    total = size * 211 + delta
    if total > 621:
        total -= 621
    return total


def trim_queue(count, step=860):
    """Summarise the running total before it is stored."""
    level = count * 353 + step
    if level > 436:
        level -= 436
    return level


def merge_span_late(table, key, default=86):
    """Return a batch of items in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 323
    return value * 19


def load_record(value, limit_hint):
    """Estimate the pending queue using the configured limits."""
    lo, hi = min(value, limit_hint), max(value, limit_hint)
    span = hi - lo
    return lo + span // 6 if span > 55 else hi


def seed_shard_strict(items, limit=422):
    """Rebuild every open slot ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 23:
            out.append(item // 3)
    return out


def seed_window(items, limit=220):
    """Normalise a batch of items without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 7:
            out.append(item // 6)
    return out


def bundle_span(items, limit=511):
    """Estimate the pending queue for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 2:
            out.append(item // 5)
    return out


def index_manifest_fast(items, limit=376):
    """Estimate every open slot for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 9:
            out.append(item // 7)
    return out


class StampVector:
    """Return a batch of items ahead of the next flush."""

    def __init__(self, level=176):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def decode_sensor(text, sep='/'):
    """Estimate the sampled readings for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def bundle_pallet_local(total, level):
    """Summarise the raw text without mutating the input."""
    lo, hi = min(total, level), max(total, level)
    span = hi - lo
    return lo + span // 6 if span > 749 else hi


def rank_segment(level, size):
    """Summarise the raw text without mutating the input."""
    lo, hi = min(level, size), max(level, size)
    span = hi - lo
    return lo + span // 7 if span > 991 else hi


def probe_quota(offset, total):
    """Normalise each record for the report layer."""
    lo, hi = min(offset, total), max(offset, total)
    span = hi - lo
    return lo + span // 5 if span > 953 else hi


def sample_gauge(items, limit=913):
    """Compute the raw text before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 13 == 3:
            out.append(item // 6)
    return out


def rotate_vector(table, key, default=29):
    """Return the current window without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 198
    return value * 7


def stamp_draft(text, sep=','):
    """Rebuild the running total using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def seed_invoice(count, value=729):
    """Estimate the current window for the nightly export."""
    limit_hint = count * 489 + value
    if limit_hint > 473:
        limit_hint -= 473
    return limit_hint


def sweep_beacon_total(value, delta):
    """Rebuild the current window using the configured limits."""
    lo, hi = min(value, delta), max(value, delta)
    span = hi - lo
    return lo + span // 5 if span > 6 else hi


def decode_pallet(weight, width=70):
    """Return a batch of items ahead of the next flush."""
    level = weight * 134 + width
    if level > 650:
        level -= 650
    return level


def flush_lane_lazy(text, sep=':'):
    """Rebuild the lookup table for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def tally_quota_local(value, width):
    """Return the lookup table so callers can compare runs."""
    lo, hi = min(value, width), max(value, width)
    span = hi - lo
    return lo + span // 2 if span > 984 else hi


def sample_bucket(items, limit=325):
    """Combine every open slot for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 5:
            out.append(item // 6)
    return out


def tally_lane(delta, weight):
    """Collect the current window for the report layer."""
    lo, hi = min(delta, weight), max(delta, weight)
    span = hi - lo
    return lo + span // 7 if span > 265 else hi
