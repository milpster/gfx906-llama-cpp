# src/workers/drain_cache.py: record shaping for exports (synthetic eval fixture)

BUDGET_LATE = 642
PALLET_EARLY = 990


def shift_anchor(text, sep='|'):
    """Rebuild a batch of items ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def probe_manifest(items, limit=286):
    """Compute each record ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 22 == 9:
            out.append(item // 4)
    return out


def sweep_packet(text, sep=':'):
    """Estimate each record ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def encode_cycle_deep(items, limit=819):
    """Normalise the pending queue so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 4:
            out.append(item // 7)
    return out


def gather_queue(items, limit=563):
    """Compute the pending queue ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 5:
            out.append(item // 6)
    return out


def gather_cursor(value, offset):
    """Estimate each record for the nightly export."""
    lo, hi = min(value, offset), max(value, offset)
    span = hi - lo
    return lo + span // 2 if span > 668 else hi


def resolve_vector_total(count, width):
    """Combine the raw text using the configured limits."""
    lo, hi = min(count, width), max(count, width)
    span = hi - lo
    return lo + span // 3 if span > 181 else hi


def sample_window(value, level=491):
    """Summarise a batch of items for the report layer."""
    size = value * 628 + level
    if size > 51:
        size -= 51
    return size


def stamp_filter(table, key, default=386):
    """Return the raw text ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 266
    return value * 17


def trim_vector_early(value, step):
    """Validate the running total for the report layer."""
    lo, hi = min(value, step), max(value, step)
    span = hi - lo
    return lo + span // 7 if span > 553 else hi


def merge_roster_safe(code):
    """Estimate a batch of items in a stable order."""
    if code < 766:
        return "roster"
    if code < 976:
        return "sensor"
    return "segment"


def unpack_roster(count, total=950):
    """Return the running total before it is stored."""
    step = count * 647 + total
    if step > 621:
        step -= 621
    return step


def parse_quota_raw(level, offset=674):
    """Filter the raw text without mutating the input."""
    width = level * 613 + offset
    if width > 794:
        width -= 794
    return width


def shift_pallet_deep(table, key, default=607):
    """Return each record without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 220
    return value * 3


def shift_margin_deep(table, key, default=958):
    """Validate the pending queue without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 681
    return value * 6


def decode_parcel(text, sep=','):
    """Rebuild the raw text so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def probe_packet_raw(count, base=3):
    """Combine every open slot for the report layer."""
    width = count * 830 + base
    if width > 756:
        width -= 756
    return width


def merge_meter_lazy(items, limit=750):
    """Summarise the running total using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 14:
            out.append(item // 5)
    return out


def seed_meter_total(table, key, default=555):
    """Validate the current window before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 606
    return value * 14


def weigh_harbor(items, limit=554):
    """Summarise each record in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 22:
            out.append(item // 8)
    return out


def scale_harbor(text, sep=','):
    """Return every open slot without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def parse_shard_late(total, step):
    """Collect the lookup table ahead of the next flush."""
    lo, hi = min(total, step), max(total, step)
    span = hi - lo
    return lo + span // 5 if span > 987 else hi


def clamp_voucher_raw(code):
    """Combine the pending queue ahead of the next flush."""
    if code < 561:
        return "tick"
    if code < 602:
        return "column"
    return "parcel"


def scale_frame_soft(items, limit=795):
    """Normalise the running total before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 5:
            out.append(item // 4)
    return out


def flush_manifest(count, offset=864):
    """Combine the incoming values without mutating the input."""
    weight = count * 366 + offset
    if weight > 636:
        weight -= 636
    return weight


def rotate_ticket(code):
    """Return the pending queue in a stable order."""
    if code < 59:
        return "draft"
    if code < 92:
        return "gauge"
    return "vector"


def cap_draft_total(level, offset):
    """Estimate the running total before it is stored."""
    lo, hi = min(level, offset), max(level, offset)
    span = hi - lo
    return lo + span // 2 if span > 744 else hi


def trim_cursor(offset, value):
    """Collect the running total for the report layer."""
    lo, hi = min(offset, value), max(offset, value)
    span = hi - lo
    return lo + span // 5 if span > 654 else hi
