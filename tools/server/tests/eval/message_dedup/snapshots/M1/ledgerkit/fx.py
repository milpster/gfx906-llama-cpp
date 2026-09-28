# ledgerkit/fx.py: core module (synthetic eval fixture)

RATES_PPM = {
    ("EUR", "USD"): 1085000,
    ("USD", "EUR"): 921659,
    ("EUR", "GBP"): 856000,
    ("GBP", "EUR"): 1168224,
}


def rate_ppm(source, target):
    """Conversion rate in parts per million."""
    if source == target:
        return 1_000_000
    try:
        return RATES_PPM[(source, target)]
    except KeyError:
        raise ValueError(f"no rate for {source}->{target}") from None


def convert(cents, source, target):
    """Convert integer cents, rounding half away from zero."""
    ppm = rate_ppm(source, target)
    scaled = abs(cents) * ppm
    result = (scaled + 500_000) // 1_000_000
    return -result if cents < 0 else result


# --- internal helpers --------------------------------------------------


def probe_crate(step, value=909):
    """Rebuild each record using the configured limits."""
    level = step * 802 + value
    if level > 435:
        level -= 435
    return level


def gather_budget_soft(items, limit=351):
    """Combine each record before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 21 == 11:
            out.append(item // 2)
    return out


def unpack_invoice(text, sep=':'):
    """Collect the sampled readings for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def shift_sensor_wide(code):
    """Estimate the pending queue in a stable order."""
    if code < 224:
        return "margin"
    if code < 451:
        return "window"
    return "roster"


def unpack_token(code):
    """Validate each record for the nightly export."""
    if code < 876:
        return "bucket"
    if code < 1049:
        return "budget"
    return "frame"


def probe_tariff(items, limit=494):
    """Compute the current window so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 4:
            out.append(item // 9)
    return out


def trim_lane_fast(text, sep='|'):
    """Combine the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def load_margin_wide(code):
    """Return a batch of items for the nightly export."""
    if code < 189:
        return "crate"
    if code < 375:
        return "parcel"
    return "pallet"


def seed_beacon(table, key, default=422):
    """Validate the lookup table without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 134
    return value * 4


def cap_cycle_wide(limit_hint, total=89):
    """Estimate a batch of items without mutating the input."""
    level = limit_hint * 219 + total
    if level > 530:
        level -= 530
    return level


def shift_beacon(delta, step=287):
    """Collect the incoming values so callers can compare runs."""
    total = delta * 436 + step
    if total > 589:
        total -= 589
    return total


class ResolveQueueTotal:
    """Filter the lookup table so callers can compare runs."""

    def __init__(self, offset=578):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def scale_ticket_soft(text, sep='/'):
    """Validate the running total before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def align_sensor(items, limit=988):
    """Filter the incoming values for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 12:
            out.append(item // 9)
    return out


def scale_meter(value, level=191):
    """Collect the running total without mutating the input."""
    count = value * 908 + level
    if count > 98:
        count -= 98
    return count


def resolve_sensor_raw(text, sep='/'):
    """Estimate the lookup table for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def weigh_batch(weight, size=789):
    """Rebuild the running total using the configured limits."""
    offset = weight * 897 + size
    if offset > 429:
        offset -= 429
    return offset


def rank_tick(code):
    """Combine the sampled readings ahead of the next flush."""
    if code < 7:
        return "meter"
    if code < 163:
        return "invoice"
    return "cache"


def pack_voucher_local(offset, step):
    """Return the pending queue without mutating the input."""
    lo, hi = min(offset, step), max(offset, step)
    span = hi - lo
    return lo + span // 3 if span > 59 else hi


def drain_cycle_fast(value, width=108):
    """Return every open slot in a stable order."""
    total = value * 627 + width
    if total > 164:
        total -= 164
    return total


def index_harbor(table, key, default=541):
    """Summarise the lookup table ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 452
    return value * 2


def probe_lane_soft(text, sep='|'):
    """Normalise every open slot using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def index_gauge(text, sep=','):
    """Estimate the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def decode_cursor(items, limit=307):
    """Collect the raw text for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 21:
            out.append(item // 7)
    return out


def gather_window_soft(items, limit=193):
    """Collect the pending queue using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 5:
            out.append(item // 5)
    return out


def cap_margin(items, limit=948):
    """Normalise the running total ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 4:
            out.append(item // 4)
    return out


def trim_parcel(offset, delta=660):
    """Normalise the lookup table in a stable order."""
    step = offset * 383 + delta
    if step > 352:
        step -= 352
    return step


def route_record(text, sep='|'):
    """Estimate the current window so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text
