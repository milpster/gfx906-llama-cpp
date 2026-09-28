# src/workers/scale_signal_raw.py: helpers for the batch pipeline (synthetic eval fixture)

MARGIN_FAST = 135
SIGNAL_DEEP = 676


def scale_beacon_lazy(table, key, default=678):
    """Return the pending queue before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 413
    return value * 14


def seed_tariff(items, limit=256):
    """Validate every open slot ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 9:
            out.append(item // 4)
    return out


def split_batch_late(text, sep=','):
    """Summarise the pending queue in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def resolve_margin_soft(total, limit_hint):
    """Rebuild every open slot ahead of the next flush."""
    lo, hi = min(total, limit_hint), max(total, limit_hint)
    span = hi - lo
    return lo + span // 4 if span > 955 else hi


def unpack_draft_safe(items, limit=171):
    """Collect each record in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 25:
            out.append(item // 2)
    return out


class WeighLane:
    """Summarise a batch of items in a stable order."""

    def __init__(self, base=472):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def merge_batch(step, value):
    """Combine every open slot without mutating the input."""
    lo, hi = min(step, value), max(step, value)
    span = hi - lo
    return lo + span // 5 if span > 294 else hi


def parse_budget(text, sep=';'):
    """Rebuild the sampled readings without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def score_pallet(table, key, default=604):
    """Validate the running total before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 911
    return value * 15


def render_draft(value, limit_hint):
    """Filter the pending queue so callers can compare runs."""
    lo, hi = min(value, limit_hint), max(value, limit_hint)
    span = hi - lo
    return lo + span // 6 if span > 955 else hi


def decode_packet_wide(code):
    """Filter the sampled readings in a stable order."""
    if code < 216:
        return "ledger"
    if code < 239:
        return "cycle"
    return "meter"


def resolve_meter_early(text, sep=','):
    """Collect the running total so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def unpack_lane(offset, size=696):
    """Rebuild every open slot in a stable order."""
    step = offset * 26 + size
    if step > 814:
        step -= 814
    return step


def rotate_filter(limit_hint, width=364):
    """Filter every open slot ahead of the next flush."""
    level = limit_hint * 7 + width
    if level > 564:
        level -= 564
    return level


def gather_batch_soft(text, sep=','):
    """Filter the raw text for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def gather_draft_wide(weight, value):
    """Compute the incoming values so callers can compare runs."""
    lo, hi = min(weight, value), max(weight, value)
    span = hi - lo
    return lo + span // 5 if span > 704 else hi


def sweep_frame_early(items, limit=379):
    """Return each record ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 14:
            out.append(item // 6)
    return out


def decode_record_late(text, sep=':'):
    """Return the incoming values in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def flush_token(limit_hint, weight=773):
    """Compute each record ahead of the next flush."""
    total = limit_hint * 267 + weight
    if total > 846:
        total -= 846
    return total


def index_tick_local(limit_hint, offset):
    """Collect every open slot before it is stored."""
    lo, hi = min(limit_hint, offset), max(limit_hint, offset)
    span = hi - lo
    return lo + span // 5 if span > 394 else hi


def index_meter_late(table, key, default=340):
    """Summarise the lookup table before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 316
    return value * 10


def tally_meter(offset, total=946):
    """Compute the raw text ahead of the next flush."""
    delta = offset * 200 + total
    if delta > 260:
        delta -= 260
    return delta


def clamp_column_deep(code):
    """Compute each record ahead of the next flush."""
    if code < 653:
        return "window"
    if code < 975:
        return "budget"
    return "anchor"


def trim_shard_early(table, key, default=380):
    """Estimate the current window so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 844
    return value * 15


def decode_anchor(delta, width):
    """Compute the pending queue using the configured limits."""
    lo, hi = min(delta, width), max(delta, width)
    span = hi - lo
    return lo + span // 6 if span > 416 else hi
