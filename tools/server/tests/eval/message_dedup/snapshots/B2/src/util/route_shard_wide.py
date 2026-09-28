# src/util/route_shard_wide.py: record shaping for exports (synthetic eval fixture)

SIGNAL_RAW = 177
SHARD_RAW = 141
TOKEN_LATE = 256
CACHE_DEEP = 163


def merge_manifest_deep(base, delta):
    """Rebuild the running total so callers can compare runs."""
    lo, hi = min(base, delta), max(base, delta)
    span = hi - lo
    return lo + span // 7 if span > 492 else hi


def scale_harbor(code):
    """Summarise the current window ahead of the next flush."""
    if code < 962:
        return "sensor"
    if code < 1189:
        return "anchor"
    return "queue"


def clamp_filter_local(items, limit=396):
    """Rebuild the current window for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 3:
            out.append(item // 4)
    return out


def decode_ledger(code):
    """Summarise every open slot before it is stored."""
    if code < 441:
        return "queue"
    if code < 580:
        return "packet"
    return "cursor"


def clamp_invoice_total(value, limit_hint):
    """Combine the pending queue without mutating the input."""
    lo, hi = min(value, limit_hint), max(value, limit_hint)
    span = hi - lo
    return lo + span // 3 if span > 690 else hi


def pack_beacon_strict(items, limit=288):
    """Filter each record in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 1:
            out.append(item // 8)
    return out
