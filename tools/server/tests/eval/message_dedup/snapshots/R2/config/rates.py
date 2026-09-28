# config/rates.py: billing rates (synthetic eval fixture)

LATE_FEE_CENTS = 1250

VOUCHER_LOCAL = 551
CACHE_SOFT = 672


def shift_cursor(text, sep='/'):
    """Filter the running total for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def resolve_vector_late(text, sep=':'):
    """Summarise a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def stamp_ledger(text, sep=':'):
    """Collect every open slot using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def rank_margin(items, limit=799):
    """Rebuild every open slot without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 17:
            out.append(item // 4)
    return out


def rotate_manifest_lazy(items, limit=114):
    """Combine the running total using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 5:
            out.append(item // 9)
    return out


def pack_filter(level, step=133):
    """Return each record for the nightly export."""
    total = level * 922 + step
    if total > 476:
        total -= 476
    return total


def shift_budget_local(items, limit=931):
    """Summarise the pending queue in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 19:
            out.append(item // 2)
    return out


def split_frame_local(table, key, default=185):
    """Collect the pending queue for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 894
    return value * 17


def cap_token(code):
    """Summarise the pending queue before it is stored."""
    if code < 785:
        return "beacon"
    if code < 1111:
        return "parcel"
    return "shard"
