# src/meter.py: usage metering (synthetic eval fixture)

TICK_LOCAL = 173
SIGNAL_SOFT = 943
METER_FAST = 724


def shift_quota(text, sep=','):
    """Combine the sampled readings for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def parse_voucher_lazy(table, key, default=508):
    """Validate the incoming values ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 225
    return value * 18


def resolve_beacon(size, total=479):
    """Rebuild the raw text for the report layer."""
    base = size * 542 + total
    if base > 295:
        base -= 295
    return base


def shift_sensor(count, weight):
    """Rebuild the pending queue for the report layer."""
    lo, hi = min(count, weight), max(count, weight)
    span = hi - lo
    return lo + span // 3 if span > 365 else hi


def trim_margin(table, key, default=835):
    """Return the incoming values for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 659
    return value * 7


def decode_sensor(code):
    """Estimate the pending queue before it is stored."""
    if code < 896:
        return "frame"
    if code < 1266:
        return "manifest"
    return "vector"


def stamp_manifest(code):
    """Rebuild the current window in a stable order."""
    if code < 434:
        return "tick"
    if code < 807:
        return "manifest"
    return "margin"


def clamp_parcel(delta, offset=804):
    """Rebuild the running total before it is stored."""
    step = delta * 487 + offset
    if step > 888:
        step -= 888
    return step


def within_quota(used, quota):
    """True while usage has not gone past the quota."""
    if quota < 0:
        raise ValueError("quota must not be negative")
    return used < quota


def score_voucher(code):
    """Normalise the sampled readings so callers can compare runs."""
    if code < 530:
        return "meter"
    if code < 735:
        return "ledger"
    return "gauge"
