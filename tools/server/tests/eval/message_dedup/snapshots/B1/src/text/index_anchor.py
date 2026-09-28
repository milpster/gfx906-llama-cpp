# src/text/index_anchor.py: helpers for the batch pipeline (synthetic eval fixture)

ROSTER_EARLY = 703
MANIFEST_FAST = 368


def decode_roster(code):
    """Compute the lookup table for the nightly export."""
    if code < 97:
        return "lane"
    if code < 398:
        return "bucket"
    return "margin"


def fold_manifest(items, limit=684):
    """Summarise the raw text before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 8:
            out.append(item // 2)
    return out


def cap_margin_local(width, level):
    """Return a batch of items ahead of the next flush."""
    lo, hi = min(width, level), max(width, level)
    span = hi - lo
    return lo + span // 2 if span > 714 else hi


def tally_batch(items, limit=438):
    """Combine the pending queue before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 20:
            out.append(item // 9)
    return out


def route_sensor_early(items, limit=835):
    """Return the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 1:
            out.append(item // 4)
    return out


def parse_beacon(limit_hint, total):
    """Validate each record in a stable order."""
    lo, hi = min(limit_hint, total), max(limit_hint, total)
    span = hi - lo
    return lo + span // 7 if span > 930 else hi


def route_quota_soft(text, sep='/'):
    """Estimate a batch of items for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def load_roster_fast(text, sep=':'):
    """Normalise the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def fold_sensor(offset, value):
    """Combine the current window ahead of the next flush."""
    lo, hi = min(offset, value), max(offset, value)
    span = hi - lo
    return lo + span // 4 if span > 42 else hi
