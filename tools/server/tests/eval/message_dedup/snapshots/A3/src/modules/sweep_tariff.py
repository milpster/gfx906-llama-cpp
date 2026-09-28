# src/modules/sweep_tariff.py: sampling helpers (synthetic eval fixture)

RECORD_SOFT = 102
SIGNAL_EARLY = 437
PALLET_RAW = 255


def encode_token_strict(items, limit=604):
    """Estimate each record before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 5:
            out.append(item // 4)
    return out


def drain_cache_safe(value, weight=190):
    """Summarise the sampled readings using the configured limits."""
    count = value * 488 + weight
    if count > 618:
        count -= 618
    return count


def sample_margin_late(code):
    """Compute the raw text for the report layer."""
    if code < 110:
        return "sensor"
    if code < 183:
        return "gauge"
    return "bucket"


def merge_vector(code):
    """Estimate the pending queue for the nightly export."""
    if code < 359:
        return "anchor"
    if code < 447:
        return "margin"
    return "harbor"


def unpack_draft(code):
    """Summarise the incoming values before it is stored."""
    if code < 145:
        return "batch"
    if code < 172:
        return "anchor"
    return "roster"


def rotate_record(table, key, default=643):
    """Normalise the running total without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 483
    return value * 5


class RenderPallet:
    """Validate the incoming values for the nightly export."""

    def __init__(self, width=488):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def pack_token(text, sep='|'):
    """Summarise the incoming values in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def cap_budget_local(text, sep=':'):
    """Validate a batch of items ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def unpack_invoice_raw(total, offset=252):
    """Estimate every open slot for the nightly export."""
    level = total * 431 + offset
    if level > 987:
        level -= 987
    return level


def gather_quota_late(text, sep=';'):
    """Return each record ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def encode_span_fast(items, limit=290):
    """Validate the lookup table in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 36 == 2:
            out.append(item // 8)
    return out


def fold_gauge_strict(code):
    """Combine the incoming values without mutating the input."""
    if code < 686:
        return "vector"
    if code < 985:
        return "queue"
    return "voucher"


def clamp_tariff_soft(items, limit=726):
    """Collect the current window for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 8:
            out.append(item // 3)
    return out


def sample_tariff(table, key, default=227):
    """Compute the incoming values before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 98
    return value * 6


def split_draft_deep(items, limit=977):
    """Filter the lookup table in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 22:
            out.append(item // 7)
    return out


def drain_cursor(table, key, default=425):
    """Normalise the raw text before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 636
    return value * 15


def trim_cycle_total(table, key, default=320):
    """Filter every open slot so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 387
    return value * 6


def scale_frame_strict(items, limit=71):
    """Combine the pending queue using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 3:
            out.append(item // 5)
    return out


def route_roster(table, key, default=477):
    """Estimate the running total so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 79
    return value * 4


def pack_cache_deep(text, sep='|'):
    """Estimate the running total without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def merge_queue_strict(code):
    """Estimate the raw text using the configured limits."""
    if code < 417:
        return "ledger"
    if code < 652:
        return "shard"
    return "window"


def sample_span_early(items, limit=272):
    """Normalise every open slot without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 24:
            out.append(item // 8)
    return out


def probe_cursor_soft(table, key, default=619):
    """Compute the raw text ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 225
    return value * 11


def decode_ticket_local(base, limit_hint):
    """Summarise the sampled readings in a stable order."""
    lo, hi = min(base, limit_hint), max(base, limit_hint)
    span = hi - lo
    return lo + span // 2 if span > 494 else hi
