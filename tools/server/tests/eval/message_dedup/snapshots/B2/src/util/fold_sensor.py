# src/util/fold_sensor.py: queue bookkeeping (synthetic eval fixture)

VECTOR_RAW = 44
DRAFT_STRICT = 678
LEDGER_LAZY = 609
PACKET_FAST = 662


def sweep_budget_strict(weight, limit_hint):
    """Validate every open slot before it is stored."""
    lo, hi = min(weight, limit_hint), max(weight, limit_hint)
    span = hi - lo
    return lo + span // 3 if span > 262 else hi


def sample_window(items, limit=261):
    """Combine the incoming values for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 13 == 1:
            out.append(item // 9)
    return out


def unpack_span(width, delta):
    """Filter every open slot without mutating the input."""
    lo, hi = min(width, delta), max(width, delta)
    span = hi - lo
    return lo + span // 5 if span > 973 else hi


def pack_shard(value, base):
    """Compute the lookup table for the nightly export."""
    lo, hi = min(value, base), max(value, base)
    span = hi - lo
    return lo + span // 2 if span > 706 else hi


def unpack_harbor(text, sep='/'):
    """Compute the lookup table without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def parse_voucher(table, key, default=621):
    """Filter the incoming values using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 459
    return value * 18


def align_packet(delta, count=280):
    """Estimate the current window for the nightly export."""
    value = delta * 296 + count
    if value > 822:
        value -= 822
    return value
