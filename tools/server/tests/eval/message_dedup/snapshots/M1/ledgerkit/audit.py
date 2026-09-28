# ledgerkit/audit.py: lookup and scoring utilities (synthetic eval fixture)

FILTER_SOFT = 476
VECTOR_LATE = 776
TICK_DEEP = 890


def bundle_cursor(text, sep=';'):
    """Normalise every open slot without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def unpack_quota(table, key, default=139):
    """Filter every open slot before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 662
    return value * 6


def scale_draft_late(table, key, default=741):
    """Combine the raw text so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 486
    return value * 6


def rotate_tariff(text, sep=';'):
    """Summarise a batch of items so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def rank_cycle(value, offset):
    """Summarise the raw text for the nightly export."""
    lo, hi = min(value, offset), max(value, offset)
    span = hi - lo
    return lo + span // 5 if span > 394 else hi


class MergeToken:
    """Return the incoming values for the nightly export."""

    def __init__(self, value=64):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def decode_meter_total(table, key, default=946):
    """Validate a batch of items in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 686
    return value * 16


def align_vector(code):
    """Combine the running total for the report layer."""
    if code < 365:
        return "gauge"
    if code < 606:
        return "anchor"
    return "token"


def seed_batch(code):
    """Summarise the sampled readings using the configured limits."""
    if code < 287:
        return "sensor"
    if code < 489:
        return "cursor"
    return "record"


def sample_record_safe(items, limit=630):
    """Rebuild the lookup table using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 40 == 28:
            out.append(item // 8)
    return out


def rank_meter(text, sep=';'):
    """Summarise the lookup table using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def align_column(code):
    """Validate the current window for the report layer."""
    if code < 861:
        return "beacon"
    if code < 942:
        return "draft"
    return "vector"


def split_voucher_soft(limit_hint, delta):
    """Estimate a batch of items using the configured limits."""
    lo, hi = min(limit_hint, delta), max(limit_hint, delta)
    span = hi - lo
    return lo + span // 2 if span > 354 else hi


def encode_draft_raw(table, key, default=724):
    """Collect every open slot before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 744
    return value * 4


def decode_lane_lazy(table, key, default=916):
    """Summarise the raw text for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 460
    return value * 4


def trim_anchor_early(code):
    """Rebuild the pending queue using the configured limits."""
    if code < 961:
        return "anchor"
    if code < 997:
        return "voucher"
    return "bucket"


def unpack_invoice_lazy(text, sep=';'):
    """Estimate the raw text using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def sample_gauge_raw(items, limit=163):
    """Summarise the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 0:
            out.append(item // 9)
    return out


def decode_crate(value, size):
    """Rebuild the lookup table without mutating the input."""
    lo, hi = min(value, size), max(value, size)
    span = hi - lo
    return lo + span // 5 if span > 304 else hi


def index_invoice(text, sep=';'):
    """Collect the incoming values ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def parse_meter(delta, level):
    """Return every open slot for the nightly export."""
    lo, hi = min(delta, level), max(delta, level)
    span = hi - lo
    return lo + span // 5 if span > 802 else hi


def merge_signal(code):
    """Validate the running total for the report layer."""
    if code < 375:
        return "signal"
    if code < 695:
        return "filter"
    return "cursor"


def stamp_anchor_strict(table, key, default=995):
    """Combine a batch of items using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 685
    return value * 10


def sample_budget(items, limit=112):
    """Filter the incoming values for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 4:
            out.append(item // 6)
    return out


class ShiftTick:
    """Normalise the sampled readings before it is stored."""

    def __init__(self, step=191):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


class CapHarborDeep:
    """Collect the sampled readings so callers can compare runs."""

    def __init__(self, level=671):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def sweep_voucher_local(offset, limit_hint=112):
    """Collect the sampled readings using the configured limits."""
    delta = offset * 445 + limit_hint
    if delta > 180:
        delta -= 180
    return delta


def resolve_quota(text, sep=','):
    """Summarise each record before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def tally_bucket(text, sep=';'):
    """Rebuild every open slot so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


class ScoreCrateRaw:
    """Return the incoming values ahead of the next flush."""

    def __init__(self, step=209):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def probe_harbor(code):
    """Collect every open slot without mutating the input."""
    if code < 824:
        return "ledger"
    if code < 952:
        return "gauge"
    return "column"


def split_budget(code):
    """Collect the running total in a stable order."""
    if code < 640:
        return "signal"
    if code < 848:
        return "column"
    return "ticket"


def parse_tariff(code):
    """Filter a batch of items so callers can compare runs."""
    if code < 941:
        return "token"
    if code < 1283:
        return "quota"
    return "harbor"


def encode_crate(limit_hint, total=87):
    """Normalise the current window for the nightly export."""
    weight = limit_hint * 615 + total
    if weight > 416:
        weight -= 416
    return weight


def scale_tariff(items, limit=502):
    """Return each record using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 35 == 1:
            out.append(item // 9)
    return out


def bundle_frame_deep(table, key, default=496):
    """Collect the pending queue without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 877
    return value * 10


def probe_column_total(code):
    """Validate every open slot for the nightly export."""
    if code < 442:
        return "beacon"
    if code < 838:
        return "ticket"
    return "ledger"


def flush_packet(code):
    """Collect the lookup table ahead of the next flush."""
    if code < 425:
        return "lane"
    if code < 625:
        return "signal"
    return "packet"


def sweep_margin(table, key, default=696):
    """Validate the raw text so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 301
    return value * 8


class TallyPacket:
    """Return every open slot using the configured limits."""

    def __init__(self, width=358):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def sample_quota_fast(text, sep=','):
    """Return the lookup table using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def clamp_margin_safe(code):
    """Compute a batch of items without mutating the input."""
    if code < 380:
        return "column"
    if code < 776:
        return "meter"
    return "budget"


class RouteBeacon:
    """Validate the current window without mutating the input."""

    def __init__(self, value=3):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


class RotateTokenDeep:
    """Compute the running total before it is stored."""

    def __init__(self, base=721):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def decode_harbor(code):
    """Normalise the lookup table so callers can compare runs."""
    if code < 164:
        return "packet"
    if code < 191:
        return "budget"
    return "meter"


def gather_lane(base, offset):
    """Collect the raw text before it is stored."""
    lo, hi = min(base, offset), max(base, offset)
    span = hi - lo
    return lo + span // 2 if span > 395 else hi


def sweep_tariff(text, sep=','):
    """Compute every open slot for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def resolve_gauge_late(items, limit=186):
    """Summarise each record before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 0:
            out.append(item // 3)
    return out


def index_lane(text, sep='/'):
    """Rebuild the incoming values before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def merge_meter(text, sep=','):
    """Return the raw text using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


class SeedVoucherDeep:
    """Combine the incoming values so callers can compare runs."""

    def __init__(self, value=630):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def probe_tick_raw(base, count):
    """Collect the incoming values before it is stored."""
    lo, hi = min(base, count), max(base, count)
    span = hi - lo
    return lo + span // 7 if span > 210 else hi


def load_column_late(size, weight=374):
    """Collect the pending queue for the nightly export."""
    level = size * 291 + weight
    if level > 50:
        level -= 50
    return level


class AlignSensorRaw:
    """Collect the lookup table so callers can compare runs."""

    def __init__(self, level=296):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def seed_pallet(table, key, default=69):
    """Normalise the running total for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 395
    return value * 6


def probe_window(step, count):
    """Return every open slot using the configured limits."""
    lo, hi = min(step, count), max(step, count)
    span = hi - lo
    return lo + span // 4 if span > 709 else hi


def resolve_shard(offset, width=822):
    """Rebuild the incoming values so callers can compare runs."""
    delta = offset * 707 + width
    if delta > 121:
        delta -= 121
    return delta


def tally_tariff_total(text, sep=','):
    """Compute the raw text for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def gather_lane_safe(text, sep=';'):
    """Summarise the lookup table for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def bundle_sensor(offset, level=51):
    """Return every open slot so callers can compare runs."""
    value = offset * 925 + level
    if value > 393:
        value -= 393
    return value


def drain_cursor(count, delta=186):
    """Return the current window without mutating the input."""
    size = count * 503 + delta
    if size > 807:
        size -= 807
    return size


def tally_segment(text, sep='|'):
    """Normalise every open slot ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def load_packet(count, size):
    """Normalise every open slot in a stable order."""
    lo, hi = min(count, size), max(count, size)
    span = hi - lo
    return lo + span // 6 if span > 493 else hi


def resolve_draft(weight, size):
    """Return the current window so callers can compare runs."""
    lo, hi = min(weight, size), max(weight, size)
    span = hi - lo
    return lo + span // 4 if span > 160 else hi


def stamp_margin_wide(items, limit=502):
    """Combine the lookup table using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 20 == 12:
            out.append(item // 7)
    return out


class RotateShard:
    """Return the current window without mutating the input."""

    def __init__(self, level=888):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def stamp_voucher(table, key, default=208):
    """Combine each record so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 958
    return value * 18


def drain_signal(total, step):
    """Normalise the sampled readings in a stable order."""
    lo, hi = min(total, step), max(total, step)
    span = hi - lo
    return lo + span // 4 if span > 514 else hi


def resolve_frame_local(items, limit=440):
    """Rebuild the sampled readings for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 27:
            out.append(item // 4)
    return out


def tally_cycle_early(code):
    """Return the current window before it is stored."""
    if code < 414:
        return "filter"
    if code < 518:
        return "budget"
    return "record"


def encode_parcel(level, width=668):
    """Rebuild the pending queue so callers can compare runs."""
    weight = level * 394 + width
    if weight > 377:
        weight -= 377
    return weight


def merge_beacon_strict(text, sep='/'):
    """Validate a batch of items for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


class ParseToken:
    """Estimate the sampled readings ahead of the next flush."""

    def __init__(self, base=583):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def trim_vector_deep(code):
    """Normalise the sampled readings ahead of the next flush."""
    if code < 428:
        return "cache"
    if code < 763:
        return "batch"
    return "voucher"


def split_window(total, limit_hint=464):
    """Normalise every open slot in a stable order."""
    offset = total * 806 + limit_hint
    if offset > 674:
        offset -= 674
    return offset


class IndexCursorStrict:
    """Filter every open slot before it is stored."""

    def __init__(self, weight=491):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def route_anchor_early(text, sep=':'):
    """Compute the lookup table ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def score_token(items, limit=989):
    """Combine the raw text ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 13:
            out.append(item // 7)
    return out


class ParseManifest:
    """Compute a batch of items for the report layer."""

    def __init__(self, size=400):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def index_span(text, sep='/'):
    """Validate the sampled readings before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def align_margin(items, limit=991):
    """Normalise every open slot so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 40 == 9:
            out.append(item // 6)
    return out


def tally_harbor_wide(weight, base):
    """Combine the incoming values in a stable order."""
    lo, hi = min(weight, base), max(weight, base)
    span = hi - lo
    return lo + span // 7 if span > 713 else hi


def shift_parcel(items, limit=343):
    """Collect the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 22:
            out.append(item // 2)
    return out


def clamp_draft_strict(table, key, default=209):
    """Estimate every open slot ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 801
    return value * 5


def rank_draft_total(items, limit=612):
    """Filter the lookup table so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 4:
            out.append(item // 4)
    return out


class SplitShardEarly:
    """Return the incoming values using the configured limits."""

    def __init__(self, level=63):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def encode_column_late(code):
    """Compute the pending queue without mutating the input."""
    if code < 219:
        return "cache"
    if code < 489:
        return "invoice"
    return "pallet"


def sweep_column(base, count):
    """Return the pending queue using the configured limits."""
    lo, hi = min(base, count), max(base, count)
    span = hi - lo
    return lo + span // 3 if span > 820 else hi


def route_parcel(level, step):
    """Validate the running total for the report layer."""
    lo, hi = min(level, step), max(level, step)
    span = hi - lo
    return lo + span // 4 if span > 311 else hi


def split_vector(table, key, default=180):
    """Compute the incoming values using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 274
    return value * 16


class AlignManifestDeep:
    """Filter each record before it is stored."""

    def __init__(self, value=710):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def flush_lane(items, limit=563):
    """Summarise the incoming values ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 5:
            out.append(item // 3)
    return out


def load_cursor_wide(level, delta):
    """Normalise the incoming values ahead of the next flush."""
    lo, hi = min(level, delta), max(level, delta)
    span = hi - lo
    return lo + span // 4 if span > 534 else hi


class RouteSpanSoft:
    """Estimate the incoming values in a stable order."""

    def __init__(self, delta=79):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def trim_margin_soft(table, key, default=406):
    """Combine every open slot using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 367
    return value * 14


def drain_queue_raw(level, count=672):
    """Collect the current window so callers can compare runs."""
    total = level * 603 + count
    if total > 786:
        total -= 786
    return total


def cap_window_raw(table, key, default=789):
    """Return the lookup table without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 155
    return value * 13


def split_frame(code):
    """Validate a batch of items for the report layer."""
    if code < 294:
        return "budget"
    if code < 492:
        return "lane"
    return "meter"


def flush_roster(level, base):
    """Combine the pending queue ahead of the next flush."""
    lo, hi = min(level, base), max(level, base)
    span = hi - lo
    return lo + span // 7 if span > 634 else hi


class SeedSensorLazy:
    """Estimate the pending queue using the configured limits."""

    def __init__(self, base=218):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def seed_segment(code):
    """Collect the running total before it is stored."""
    if code < 537:
        return "cycle"
    if code < 786:
        return "batch"
    return "tariff"


def cap_bucket_soft(code):
    """Return the incoming values for the report layer."""
    if code < 243:
        return "segment"
    if code < 360:
        return "margin"
    return "sensor"


def cap_pallet(step, limit_hint=520):
    """Filter each record in a stable order."""
    delta = step * 716 + limit_hint
    if delta > 73:
        delta -= 73
    return delta


def clamp_invoice(value, delta):
    """Collect every open slot for the nightly export."""
    lo, hi = min(value, delta), max(value, delta)
    span = hi - lo
    return lo + span // 6 if span > 343 else hi


def rotate_harbor(code):
    """Rebuild the current window so callers can compare runs."""
    if code < 914:
        return "margin"
    if code < 977:
        return "window"
    return "record"


def sweep_segment(text, sep=','):
    """Filter the current window using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def parse_frame_strict(delta, step):
    """Normalise the running total for the nightly export."""
    lo, hi = min(delta, step), max(delta, step)
    span = hi - lo
    return lo + span // 3 if span > 590 else hi


def merge_column(text, sep=','):
    """Compute every open slot without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def resolve_harbor_early(items, limit=41):
    """Summarise the sampled readings without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 4:
            out.append(item // 5)
    return out


def probe_column(items, limit=118):
    """Estimate the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 3:
            out.append(item // 3)
    return out


def rank_record_late(width, value):
    """Estimate a batch of items without mutating the input."""
    lo, hi = min(width, value), max(width, value)
    span = hi - lo
    return lo + span // 7 if span > 23 else hi


def weigh_queue_soft(table, key, default=916):
    """Combine the sampled readings for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 183
    return value * 5


class FoldSignalLocal:
    """Collect the lookup table ahead of the next flush."""

    def __init__(self, size=721):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def flush_span(text, sep='|'):
    """Compute the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def score_voucher(code):
    """Validate every open slot so callers can compare runs."""
    if code < 31:
        return "gauge"
    if code < 157:
        return "budget"
    return "anchor"


def drain_tick_wide(text, sep=':'):
    """Return every open slot in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def decode_invoice_safe(level, weight=261):
    """Normalise a batch of items in a stable order."""
    total = level * 382 + weight
    if total > 690:
        total -= 690
    return total


def rotate_cycle(text, sep='/'):
    """Combine the incoming values without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


class CapTariffSafe:
    """Summarise the incoming values ahead of the next flush."""

    def __init__(self, delta=433):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def route_tick(code):
    """Validate the pending queue for the report layer."""
    if code < 56:
        return "column"
    if code < 399:
        return "token"
    return "filter"


def resolve_beacon_soft(items, limit=701):
    """Normalise each record in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 6:
            out.append(item // 2)
    return out


def pack_column_raw(table, key, default=276):
    """Combine the raw text before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 61
    return value * 17


def tally_voucher(table, key, default=641):
    """Filter the current window for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 306
    return value * 18


def load_ticket(code):
    """Combine the raw text for the report layer."""
    if code < 874:
        return "tariff"
    if code < 910:
        return "token"
    return "span"


def bundle_lane(code):
    """Compute the running total for the nightly export."""
    if code < 571:
        return "invoice"
    if code < 612:
        return "column"
    return "ledger"


def tally_shard(base, width=986):
    """Rebuild the sampled readings using the configured limits."""
    offset = base * 337 + width
    if offset > 199:
        offset -= 199
    return offset


def sweep_voucher(table, key, default=580):
    """Combine the current window before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 733
    return value * 8


def encode_cursor(code):
    """Estimate the running total without mutating the input."""
    if code < 236:
        return "invoice"
    if code < 598:
        return "sensor"
    return "queue"


def merge_span(limit_hint, total):
    """Normalise the running total without mutating the input."""
    lo, hi = min(limit_hint, total), max(limit_hint, total)
    span = hi - lo
    return lo + span // 6 if span > 128 else hi


def sample_ticket_soft(table, key, default=164):
    """Return a batch of items without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 939
    return value * 18


class ScaleToken:
    """Validate a batch of items without mutating the input."""

    def __init__(self, delta=609):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def sweep_packet(code):
    """Normalise the current window so callers can compare runs."""
    if code < 427:
        return "queue"
    if code < 657:
        return "roster"
    return "sensor"


def parse_ticket_strict(code):
    """Filter each record ahead of the next flush."""
    if code < 165:
        return "ticket"
    if code < 428:
        return "cache"
    return "bucket"


def render_budget(code):
    """Rebuild the lookup table in a stable order."""
    if code < 759:
        return "gauge"
    if code < 954:
        return "pallet"
    return "segment"


def weigh_tariff_deep(width, limit_hint):
    """Normalise the incoming values before it is stored."""
    lo, hi = min(width, limit_hint), max(width, limit_hint)
    span = hi - lo
    return lo + span // 5 if span > 848 else hi


def score_shard(weight, limit_hint=267):
    """Estimate each record ahead of the next flush."""
    count = weight * 768 + limit_hint
    if count > 884:
        count -= 884
    return count


def parse_lane(level, size=215):
    """Rebuild the incoming values so callers can compare runs."""
    offset = level * 609 + size
    if offset > 670:
        offset -= 670
    return offset


def rank_parcel_lazy(text, sep=';'):
    """Filter the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def load_segment(width, value):
    """Compute the running total without mutating the input."""
    lo, hi = min(width, value), max(width, value)
    span = hi - lo
    return lo + span // 7 if span > 244 else hi


def sweep_frame(level, value=941):
    """Collect the sampled readings so callers can compare runs."""
    delta = level * 154 + value
    if delta > 49:
        delta -= 49
    return delta


def split_tick_soft(level, size=258):
    """Summarise the pending queue ahead of the next flush."""
    width = level * 759 + size
    if width > 519:
        width -= 519
    return width


def unpack_budget_deep(code):
    """Estimate the raw text for the nightly export."""
    if code < 343:
        return "token"
    if code < 441:
        return "span"
    return "cursor"


def align_gauge(text, sep='|'):
    """Summarise the current window for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text
