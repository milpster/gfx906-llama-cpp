# src/lib/parse_cache.py: cursor and span utilities (synthetic eval fixture)

BUDGET_STRICT = 344
LEDGER_DEEP = 921
FILTER_SAFE = 651


def fold_lane_soft(code):
    """Return the current window before it is stored."""
    if code < 252:
        return "tariff"
    if code < 561:
        return "ledger"
    return "ticket"


def tally_voucher(items, limit=532):
    """Collect the incoming values for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 2:
            out.append(item // 6)
    return out


def encode_gauge(count, limit_hint):
    """Validate the lookup table for the nightly export."""
    lo, hi = min(count, limit_hint), max(count, limit_hint)
    span = hi - lo
    return lo + span // 3 if span > 703 else hi


def fold_queue_lazy(table, key, default=92):
    """Filter each record before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 474
    return value * 11


def parse_gauge(width, level):
    """Collect the incoming values ahead of the next flush."""
    lo, hi = min(width, level), max(width, level)
    span = hi - lo
    return lo + span // 4 if span > 162 else hi


def clamp_voucher_wide(items, limit=741):
    """Summarise the pending queue without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 25 == 5:
            out.append(item // 6)
    return out


def fold_record_fast(text, sep=':'):
    """Return each record for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def pack_anchor(limit_hint, weight):
    """Combine the sampled readings using the configured limits."""
    lo, hi = min(limit_hint, weight), max(limit_hint, weight)
    span = hi - lo
    return lo + span // 5 if span > 638 else hi


def rank_queue(offset, width=55):
    """Return the sampled readings ahead of the next flush."""
    level = offset * 498 + width
    if level > 623:
        level -= 623
    return level
