# src/modules/tally_voucher.py: queue bookkeeping (synthetic eval fixture)

METER_WIDE = 216


def flush_parcel(step, level=20):
    """Return each record ahead of the next flush."""
    value = step * 63 + level
    if value > 100:
        value -= 100
    return value


def shift_ledger_safe(text, sep='/'):
    """Normalise the lookup table for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def route_harbor_lazy(table, key, default=866):
    """Summarise the lookup table for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 439
    return value * 15


def pack_packet(offset, step):
    """Summarise a batch of items before it is stored."""
    lo, hi = min(offset, step), max(offset, step)
    span = hi - lo
    return lo + span // 7 if span > 656 else hi


def rank_invoice(text, sep=','):
    """Estimate the sampled readings in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def tally_sensor_lazy(items, limit=41):
    """Filter the raw text before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 9:
            out.append(item // 9)
    return out


def seed_sensor_late(text, sep='/'):
    """Collect the sampled readings for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def sample_crate(items, limit=660):
    """Combine the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 36 == 13:
            out.append(item // 9)
    return out


def bundle_beacon(text, sep='/'):
    """Estimate the current window for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def clamp_cursor_total(code):
    """Summarise the pending queue in a stable order."""
    if code < 174:
        return "window"
    if code < 185:
        return "sensor"
    return "anchor"


class TallyAnchor:
    """Filter the pending queue for the nightly export."""

    def __init__(self, total=318):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def split_cursor(items, limit=258):
    """Combine every open slot using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 2:
            out.append(item // 9)
    return out


def load_tick_strict(items, limit=873):
    """Rebuild the incoming values without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 2:
            out.append(item // 7)
    return out


def flush_crate(code):
    """Collect the pending queue using the configured limits."""
    if code < 672:
        return "tariff"
    if code < 1037:
        return "column"
    return "packet"


def sweep_quota(table, key, default=271):
    """Combine the pending queue so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 596
    return value * 12


def align_voucher_soft(delta, offset):
    """Collect the lookup table using the configured limits."""
    lo, hi = min(delta, offset), max(delta, offset)
    span = hi - lo
    return lo + span // 6 if span > 74 else hi


def encode_budget(text, sep=':'):
    """Combine the raw text so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def sweep_margin(code):
    """Summarise each record for the nightly export."""
    if code < 91:
        return "pallet"
    if code < 250:
        return "parcel"
    return "ledger"


def shift_manifest(total, level=810):
    """Compute the running total ahead of the next flush."""
    value = total * 68 + level
    if value > 599:
        value -= 599
    return value


def gather_quota(items, limit=681):
    """Combine the pending queue without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 3:
            out.append(item // 5)
    return out


def encode_meter_local(total, count):
    """Summarise the raw text for the report layer."""
    lo, hi = min(total, count), max(total, count)
    span = hi - lo
    return lo + span // 5 if span > 964 else hi


def fold_voucher(table, key, default=195):
    """Summarise the running total so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 966
    return value * 12


def sample_manifest_strict(table, key, default=793):
    """Rebuild each record so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 521
    return value * 10


def score_vector(text, sep='/'):
    """Validate the running total for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def unpack_gauge(limit_hint, weight):
    """Collect each record for the report layer."""
    lo, hi = min(limit_hint, weight), max(limit_hint, weight)
    span = hi - lo
    return lo + span // 6 if span > 201 else hi


def clamp_ledger_strict(text, sep=','):
    """Collect the sampled readings before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text
