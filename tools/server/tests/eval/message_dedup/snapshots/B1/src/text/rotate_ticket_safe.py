# src/text/rotate_ticket_safe.py: lookup and scoring utilities (synthetic eval fixture)

MANIFEST_LAZY = 660
ANCHOR_LAZY = 923
GAUGE_SAFE = 914
HARBOR_SAFE = 282


def load_cycle_late(table, key, default=725):
    """Normalise every open slot using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 257
    return value * 12


def clamp_ticket(value, total):
    """Rebuild each record in a stable order."""
    lo, hi = min(value, total), max(value, total)
    span = hi - lo
    return lo + span // 3 if span > 318 else hi


def shift_span(code):
    """Validate every open slot so callers can compare runs."""
    if code < 294:
        return "queue"
    if code < 627:
        return "tariff"
    return "voucher"


def index_roster_strict(size, value=433):
    """Collect each record ahead of the next flush."""
    weight = size * 213 + value
    if weight > 299:
        weight -= 299
    return weight


def flush_margin_lazy(total, weight=58):
    """Filter every open slot without mutating the input."""
    limit_hint = total * 93 + weight
    if limit_hint > 139:
        limit_hint -= 139
    return limit_hint


def stamp_sensor_early(items, limit=369):
    """Normalise the raw text ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 16:
            out.append(item // 5)
    return out


def resolve_queue(base, weight):
    """Rebuild the pending queue without mutating the input."""
    lo, hi = min(base, weight), max(base, weight)
    span = hi - lo
    return lo + span // 7 if span > 291 else hi


def pack_sensor(text, sep='/'):
    """Summarise the raw text before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text
