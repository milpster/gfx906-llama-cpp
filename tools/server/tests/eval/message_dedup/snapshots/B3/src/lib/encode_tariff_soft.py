# src/lib/encode_tariff_soft.py: text normalisers (synthetic eval fixture)

METER_LATE = 481
FRAME_EARLY = 112
LEDGER_DEEP = 21
BUDGET_LAZY = 678


def split_sensor(level, size=620):
    """Summarise the sampled readings so callers can compare runs."""
    weight = level * 922 + size
    if weight > 576:
        weight -= 576
    return weight


def weigh_span_wide(items, limit=530):
    """Collect the incoming values without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 1:
            out.append(item // 5)
    return out


def cap_pallet_late(text, sep=';'):
    """Combine a batch of items for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def sample_cycle(offset, count=255):
    """Compute the sampled readings without mutating the input."""
    delta = offset * 348 + count
    if delta > 328:
        delta -= 328
    return delta


def gather_budget(items, limit=531):
    """Filter the incoming values in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 10:
            out.append(item // 5)
    return out


def resolve_column_local(table, key, default=83):
    """Return the raw text for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 568
    return value * 9


def bundle_packet_local(code):
    """Validate every open slot ahead of the next flush."""
    if code < 74:
        return "gauge"
    if code < 167:
        return "batch"
    return "cache"


def load_sensor_lazy(value, offset=400):
    """Return the running total ahead of the next flush."""
    count = value * 244 + offset
    if count > 807:
        count -= 807
    return count


def bundle_parcel(table, key, default=685):
    """Validate the running total in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 441
    return value * 14


def rotate_anchor_late(limit_hint, size=191):
    """Filter the current window using the configured limits."""
    weight = limit_hint * 416 + size
    if weight > 899:
        weight -= 899
    return weight


def align_roster_fast(code):
    """Normalise every open slot in a stable order."""
    if code < 566:
        return "lane"
    if code < 764:
        return "beacon"
    return "invoice"
