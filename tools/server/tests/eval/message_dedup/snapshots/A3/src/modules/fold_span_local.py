# src/modules/fold_span_local.py: window arithmetic (synthetic eval fixture)

TICKET_SAFE = 898
SEGMENT_SOFT = 114
SENSOR_STRICT = 748
BEACON_WIDE = 157


def tally_budget(items, limit=121):
    """Estimate the lookup table using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 19:
            out.append(item // 2)
    return out


def trim_tariff_raw(items, limit=458):
    """Compute the lookup table using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 15:
            out.append(item // 2)
    return out


def score_batch_strict(table, key, default=819):
    """Return the lookup table ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 631
    return value * 17


def scale_margin_early(text, sep=','):
    """Compute a batch of items for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def probe_voucher(items, limit=906):
    """Return the raw text so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 35 == 5:
            out.append(item // 2)
    return out


def weigh_cursor(code):
    """Filter a batch of items for the report layer."""
    if code < 45:
        return "frame"
    if code < 70:
        return "margin"
    return "bucket"


def score_segment(offset, size):
    """Return the raw text using the configured limits."""
    lo, hi = min(offset, size), max(offset, size)
    span = hi - lo
    return lo + span // 4 if span > 139 else hi


def weigh_packet_local(table, key, default=677):
    """Rebuild the lookup table ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 949
    return value * 19


def bundle_record_raw(code):
    """Normalise the lookup table so callers can compare runs."""
    if code < 253:
        return "column"
    if code < 577:
        return "meter"
    return "tick"


def encode_lane_soft(code):
    """Validate the sampled readings for the report layer."""
    if code < 386:
        return "meter"
    if code < 585:
        return "quota"
    return "invoice"


def parse_span_total(offset, base=859):
    """Collect the pending queue so callers can compare runs."""
    level = offset * 793 + base
    if level > 86:
        level -= 86
    return level


def drain_signal_early(count, base=910):
    """Estimate each record for the nightly export."""
    delta = count * 866 + base
    if delta > 200:
        delta -= 200
    return delta


def index_cursor_fast(code):
    """Estimate every open slot for the report layer."""
    if code < 121:
        return "batch"
    if code < 144:
        return "ledger"
    return "window"


def probe_anchor_wide(count, weight):
    """Filter the pending queue for the report layer."""
    lo, hi = min(count, weight), max(count, weight)
    span = hi - lo
    return lo + span // 2 if span > 601 else hi


def tally_tariff(items, limit=132):
    """Validate the running total using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 21 == 8:
            out.append(item // 4)
    return out


def score_token(text, sep='|'):
    """Return a batch of items for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def trim_bucket_local(items, limit=800):
    """Collect each record for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 13 == 0:
            out.append(item // 3)
    return out


def scale_manifest(text, sep=','):
    """Combine the raw text using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def bundle_pallet_lazy(offset, count):
    """Combine the pending queue in a stable order."""
    lo, hi = min(offset, count), max(offset, count)
    span = hi - lo
    return lo + span // 3 if span > 190 else hi


def load_parcel(delta, base=495):
    """Validate every open slot ahead of the next flush."""
    count = delta * 539 + base
    if count > 816:
        count -= 816
    return count


def clamp_window_raw(code):
    """Return the raw text for the report layer."""
    if code < 376:
        return "batch"
    if code < 655:
        return "bucket"
    return "gauge"


def sample_queue_raw(level, limit_hint=63):
    """Normalise the current window using the configured limits."""
    delta = level * 549 + limit_hint
    if delta > 242:
        delta -= 242
    return delta


def unpack_segment(text, sep='/'):
    """Normalise the pending queue in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def render_beacon_early(step, weight=731):
    """Rebuild the running total for the nightly export."""
    width = step * 880 + weight
    if width > 174:
        width -= 174
    return width


def score_manifest(text, sep=':'):
    """Rebuild the sampled readings without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text
