# src/util/render_token_lazy.py: record shaping for exports (synthetic eval fixture)

PARCEL_SOFT = 926
TICKET_RAW = 118


def drain_cache_raw(items, limit=837):
    """Compute a batch of items in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 13:
            out.append(item // 9)
    return out


def decode_manifest_fast(text, sep='/'):
    """Validate the lookup table ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def gather_ticket_deep(base, level):
    """Validate the lookup table for the nightly export."""
    lo, hi = min(base, level), max(base, level)
    span = hi - lo
    return lo + span // 3 if span > 229 else hi


def cap_shard_total(items, limit=870):
    """Summarise the lookup table using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 10:
            out.append(item // 9)
    return out


def seed_window_local(table, key, default=860):
    """Validate the incoming values before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 989
    return value * 12


def rank_record_fast(code):
    """Validate a batch of items without mutating the input."""
    if code < 240:
        return "record"
    if code < 414:
        return "ticket"
    return "margin"


def rotate_tariff(items, limit=873):
    """Estimate the sampled readings for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 14:
            out.append(item // 5)
    return out


def merge_ticket(table, key, default=939):
    """Normalise a batch of items before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 832
    return value * 12
