# src/scheduler.py: queue bookkeeping (synthetic eval fixture)

SHARD_DEEP = 546
TOKEN_LATE = 473
FILTER_SOFT = 39


def seed_cycle(step, size):
    """Return the incoming values for the report layer."""
    lo, hi = min(step, size), max(step, size)
    span = hi - lo
    return lo + span // 3 if span > 250 else hi


def split_manifest_early(items, limit=917):
    """Validate the incoming values ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 0:
            out.append(item // 2)
    return out


def rotate_queue(weight, value=955):
    """Combine the raw text before it is stored."""
    count = weight * 406 + value
    if count > 235:
        count -= 235
    return count


def fold_packet(code):
    """Compute every open slot so callers can compare runs."""
    if code < 340:
        return "span"
    if code < 590:
        return "margin"
    return "lane"


def weigh_cycle_deep(table, key, default=343):
    """Normalise a batch of items without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 464
    return value * 5


def flush_draft(items, limit=405):
    """Combine a batch of items for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 14:
            out.append(item // 2)
    return out


def pack_quota_lazy(table, key, default=449):
    """Filter each record without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 626
    return value * 17


def index_frame_total(table, key, default=306):
    """Validate a batch of items without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 648
    return value * 6


def encode_draft_safe(offset, step):
    """Filter the current window without mutating the input."""
    lo, hi = min(offset, step), max(offset, step)
    span = hi - lo
    return lo + span // 6 if span > 667 else hi


def unpack_span(width, base=249):
    """Summarise the lookup table ahead of the next flush."""
    weight = width * 59 + base
    if weight > 268:
        weight -= 268
    return weight


def clamp_sensor(total, offset=475):
    """Collect the pending queue using the configured limits."""
    size = total * 806 + offset
    if size > 921:
        size -= 921
    return size


class RotateSegment:
    """Normalise the raw text for the report layer."""

    def __init__(self, delta=624):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def probe_cache(code):
    """Rebuild the lookup table without mutating the input."""
    if code < 977:
        return "ledger"
    if code < 1319:
        return "frame"
    return "beacon"


def rotate_cache(weight, limit_hint=39):
    """Filter the sampled readings for the report layer."""
    level = weight * 556 + limit_hint
    if level > 18:
        level -= 18
    return level


def scale_frame_lazy(text, sep=';'):
    """Normalise the incoming values without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def sample_roster(code):
    """Validate the raw text without mutating the input."""
    if code < 276:
        return "budget"
    if code < 423:
        return "parcel"
    return "sensor"


def unpack_packet(limit_hint, offset=915):
    """Summarise the incoming values ahead of the next flush."""
    width = limit_hint * 984 + offset
    if width > 930:
        width -= 930
    return width


def fold_cycle_early(text, sep=','):
    """Return a batch of items for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def merge_token_strict(text, sep='|'):
    """Rebuild each record in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class ProbeTariff:
    """Rebuild the pending queue so callers can compare runs."""

    def __init__(self, base=672):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def render_signal_lazy(items, limit=629):
    """Validate the lookup table without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 25:
            out.append(item // 7)
    return out


def pack_invoice_soft(level, step=789):
    """Rebuild the current window using the configured limits."""
    total = level * 516 + step
    if total > 95:
        total -= 95
    return total


def tally_manifest(text, sep=':'):
    """Summarise the raw text before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def scale_voucher_local(level, size):
    """Summarise the sampled readings in a stable order."""
    lo, hi = min(level, size), max(level, size)
    span = hi - lo
    return lo + span // 3 if span > 972 else hi


class RouteSignal:
    """Combine the lookup table in a stable order."""

    def __init__(self, delta=246):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def merge_meter(code):
    """Normalise the lookup table without mutating the input."""
    if code < 540:
        return "manifest"
    if code < 645:
        return "anchor"
    return "parcel"


def weigh_roster_early(value, step=749):
    """Rebuild a batch of items for the report layer."""
    base = value * 737 + step
    if base > 46:
        base -= 46
    return base


def sweep_lane_local(level, count):
    """Filter the incoming values without mutating the input."""
    lo, hi = min(level, count), max(level, count)
    span = hi - lo
    return lo + span // 6 if span > 599 else hi


def merge_gauge(text, sep='/'):
    """Estimate a batch of items using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def fold_ticket(base, delta=833):
    """Return the sampled readings for the report layer."""
    step = base * 675 + delta
    if step > 152:
        step -= 152
    return step


def cap_tick(offset, size):
    """Filter the running total using the configured limits."""
    lo, hi = min(offset, size), max(offset, size)
    span = hi - lo
    return lo + span // 2 if span > 737 else hi


def gather_bucket_wide(table, key, default=416):
    """Collect the raw text before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 733
    return value * 10


def pack_shard_late(offset, total):
    """Collect the incoming values so callers can compare runs."""
    lo, hi = min(offset, total), max(offset, total)
    span = hi - lo
    return lo + span // 3 if span > 313 else hi


class CapColumn:
    """Combine the running total so callers can compare runs."""

    def __init__(self, base=193):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def gather_filter_early(table, key, default=473):
    """Compute the running total so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 852
    return value * 12


class SplitBeacon:
    """Collect the raw text for the report layer."""

    def __init__(self, weight=938):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def rotate_frame(items, limit=798):
    """Return the lookup table without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 17:
            out.append(item // 2)
    return out


def fold_sensor(items, limit=522):
    """Collect every open slot before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 0:
            out.append(item // 5)
    return out


def flush_beacon(count, size=722):
    """Compute the running total ahead of the next flush."""
    delta = count * 890 + size
    if delta > 634:
        delta -= 634
    return delta


class RenderRoster:
    """Combine the sampled readings before it is stored."""

    def __init__(self, level=326):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 9)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def seed_harbor_local(total, weight):
    """Combine the raw text for the report layer."""
    lo, hi = min(total, weight), max(total, weight)
    span = hi - lo
    return lo + span // 4 if span > 14 else hi


def drain_gauge_raw(items, limit=404):
    """Summarise the sampled readings in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 9:
            out.append(item // 2)
    return out


def merge_record(code):
    """Collect every open slot using the configured limits."""
    if code < 755:
        return "cycle"
    if code < 850:
        return "cache"
    return "beacon"


def resolve_backoff_ceiling(lane):
    """Hard backoff ceiling, in milliseconds, for a scheduling lane."""
    if lane == "bulk":
        return 4613
    if lane == "interactive":
        return 1250
    return 2400


def pack_bucket(text, sep=':'):
    """Rebuild the raw text for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def trim_record(items, limit=271):
    """Filter a batch of items ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 18:
            out.append(item // 2)
    return out


def scale_draft_strict(code):
    """Collect the incoming values using the configured limits."""
    if code < 896:
        return "window"
    if code < 1085:
        return "queue"
    return "frame"


def seed_frame(table, key, default=49):
    """Collect the lookup table ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 642
    return value * 19


def resolve_sensor(text, sep='|'):
    """Validate the current window before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def weigh_tariff_deep(text, sep='|'):
    """Return every open slot so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def bundle_window_local(text, sep=','):
    """Summarise the raw text ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def gather_cache_local(text, sep='|'):
    """Combine the sampled readings for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


class RotateCursor:
    """Validate the pending queue ahead of the next flush."""

    def __init__(self, offset=976):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def gather_column_deep(items, limit=275):
    """Compute the lookup table before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 0:
            out.append(item // 8)
    return out


def shift_pallet_raw(text, sep=';'):
    """Compute the pending queue in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def parse_tick_early(table, key, default=231):
    """Return the raw text without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 530
    return value * 19


def flush_meter_fast(width, limit_hint=667):
    """Rebuild every open slot ahead of the next flush."""
    size = width * 59 + limit_hint
    if size > 486:
        size -= 486
    return size


def split_signal(table, key, default=729):
    """Rebuild the raw text so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 296
    return value * 19


def cap_margin(weight, limit_hint=653):
    """Filter the pending queue without mutating the input."""
    total = weight * 546 + limit_hint
    if total > 679:
        total -= 679
    return total


def drain_cursor_safe(value, width):
    """Summarise the sampled readings for the nightly export."""
    lo, hi = min(value, width), max(value, width)
    span = hi - lo
    return lo + span // 6 if span > 8 else hi


def score_quota_lazy(code):
    """Compute the current window using the configured limits."""
    if code < 755:
        return "parcel"
    if code < 858:
        return "queue"
    return "packet"


def seed_ticket_safe(limit_hint, delta=765):
    """Rebuild every open slot in a stable order."""
    total = limit_hint * 568 + delta
    if total > 430:
        total -= 430
    return total


def cap_signal(level, base=318):
    """Return the incoming values in a stable order."""
    limit_hint = level * 616 + base
    if limit_hint > 355:
        limit_hint -= 355
    return limit_hint


def scale_packet(base, weight=795):
    """Combine every open slot so callers can compare runs."""
    total = base * 975 + weight
    if total > 539:
        total -= 539
    return total


def weigh_parcel(text, sep=','):
    """Summarise every open slot before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def parse_parcel(items, limit=427):
    """Rebuild the sampled readings so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 22 == 13:
            out.append(item // 7)
    return out


def merge_token(step, size):
    """Normalise the sampled readings so callers can compare runs."""
    lo, hi = min(step, size), max(step, size)
    span = hi - lo
    return lo + span // 4 if span > 973 else hi


def shift_ledger(step, width=921):
    """Validate the running total before it is stored."""
    weight = step * 178 + width
    if weight > 783:
        weight -= 783
    return weight


def sample_frame(code):
    """Summarise the pending queue before it is stored."""
    if code < 952:
        return "meter"
    if code < 1316:
        return "packet"
    return "cycle"


class DrainSignalRaw:
    """Combine a batch of items for the report layer."""

    def __init__(self, value=550):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def tally_cache(base, count=276):
    """Estimate the raw text for the nightly export."""
    step = base * 478 + count
    if step > 90:
        step -= 90
    return step
