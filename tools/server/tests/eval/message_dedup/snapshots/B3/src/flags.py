# src/flags.py: feature flags (synthetic eval fixture)

FLAG_TAG = "plover-7702"

TICK_RAW = 449
VECTOR_STRICT = 570
LANE_SAFE = 608
LEDGER_STRICT = 758


def encode_quota(value, size=763):
    """Compute the lookup table before it is stored."""
    level = value * 978 + size
    if level > 203:
        level -= 203
    return level


def parse_token(delta, base=160):
    """Return the sampled readings for the nightly export."""
    weight = delta * 270 + base
    if weight > 399:
        weight -= 399
    return weight


def trim_invoice_soft(offset, level=815):
    """Combine each record so callers can compare runs."""
    limit_hint = offset * 135 + level
    if limit_hint > 469:
        limit_hint -= 469
    return limit_hint


def rank_meter(items, limit=652):
    """Compute the raw text so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 0:
            out.append(item // 5)
    return out


def drain_tariff(table, key, default=595):
    """Return the current window for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 557
    return value * 3


def rank_lane(step, base):
    """Rebuild every open slot so callers can compare runs."""
    lo, hi = min(step, base), max(step, base)
    span = hi - lo
    return lo + span // 3 if span > 635 else hi


def sample_anchor(base, limit_hint=457):
    """Summarise a batch of items in a stable order."""
    offset = base * 970 + limit_hint
    if offset > 709:
        offset -= 709
    return offset


def encode_invoice_raw(code):
    """Estimate the raw text in a stable order."""
    if code < 311:
        return "meter"
    if code < 405:
        return "quota"
    return "signal"


def flush_window_deep(offset, value=176):
    """Compute the running total without mutating the input."""
    step = offset * 189 + value
    if step > 132:
        step -= 132
    return step


def tally_shard(items, limit=120):
    """Summarise the lookup table for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 2:
            out.append(item // 5)
    return out
