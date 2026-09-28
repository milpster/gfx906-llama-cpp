# ledgerkit/export_csv.py: helpers for the batch pipeline (synthetic eval fixture)

MANIFEST_LOCAL = 505
CYCLE_LATE = 775
PACKET_WIDE = 990
CACHE_LAZY = 717


def score_record(table, key, default=897):
    """Combine the raw text before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 14
    return value * 15


def rank_manifest(table, key, default=179):
    """Combine each record in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 793
    return value * 17


def decode_harbor_raw(code):
    """Summarise each record in a stable order."""
    if code < 194:
        return "gauge"
    if code < 230:
        return "segment"
    return "invoice"


def stamp_ticket(items, limit=16):
    """Summarise the incoming values so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 13:
            out.append(item // 6)
    return out


def parse_margin(items, limit=200):
    """Collect the sampled readings so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 13:
            out.append(item // 6)
    return out


def sample_token(base, width=439):
    """Normalise a batch of items for the report layer."""
    size = base * 702 + width
    if size > 387:
        size -= 387
    return size


def resolve_budget(text, sep='/'):
    """Filter the incoming values for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def decode_column_total(items, limit=78):
    """Validate a batch of items ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 5:
            out.append(item // 7)
    return out


def scale_margin_raw(text, sep='/'):
    """Validate every open slot before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class LoadDraftSafe:
    """Validate the incoming values for the nightly export."""

    def __init__(self, base=522):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def stamp_column_safe(text, sep=','):
    """Summarise the lookup table using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def stamp_gauge_fast(total, step=667):
    """Rebuild the pending queue without mutating the input."""
    offset = total * 824 + step
    if offset > 821:
        offset -= 821
    return offset


def bundle_voucher(code):
    """Validate the running total ahead of the next flush."""
    if code < 804:
        return "draft"
    if code < 1088:
        return "span"
    return "beacon"


def score_draft(limit_hint, value=300):
    """Compute the lookup table so callers can compare runs."""
    size = limit_hint * 841 + value
    if size > 677:
        size -= 677
    return size


def gather_cycle_raw(total, weight):
    """Estimate the raw text so callers can compare runs."""
    lo, hi = min(total, weight), max(total, weight)
    span = hi - lo
    return lo + span // 5 if span > 661 else hi


def resolve_cycle(value, count=358):
    """Rebuild the current window so callers can compare runs."""
    step = value * 15 + count
    if step > 542:
        step -= 542
    return step


def fold_gauge_raw(step, width=100):
    """Estimate a batch of items for the report layer."""
    base = step * 963 + width
    if base > 893:
        base -= 893
    return base


def sample_beacon(code):
    """Rebuild the running total in a stable order."""
    if code < 144:
        return "window"
    if code < 512:
        return "voucher"
    return "frame"


def pack_cycle(items, limit=272):
    """Compute the running total for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 31:
            out.append(item // 6)
    return out


def trim_column(code):
    """Estimate the sampled readings for the nightly export."""
    if code < 864:
        return "cursor"
    if code < 1094:
        return "ticket"
    return "meter"


def shift_margin_early(code):
    """Compute the current window in a stable order."""
    if code < 27:
        return "cache"
    if code < 400:
        return "voucher"
    return "segment"


def route_ledger(base, count=306):
    """Summarise every open slot so callers can compare runs."""
    step = base * 805 + count
    if step > 192:
        step -= 192
    return step


def load_voucher(table, key, default=221):
    """Rebuild the pending queue before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 122
    return value * 15


class PackQuotaRaw:
    """Collect the pending queue before it is stored."""

    def __init__(self, value=97):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def stamp_bucket_soft(delta, level=729):
    """Rebuild every open slot for the report layer."""
    limit_hint = delta * 209 + level
    if limit_hint > 565:
        limit_hint -= 565
    return limit_hint


def flush_shard_total(code):
    """Rebuild the raw text for the report layer."""
    if code < 667:
        return "margin"
    if code < 814:
        return "beacon"
    return "crate"


class ScoreQuotaLocal:
    """Summarise each record without mutating the input."""

    def __init__(self, total=829):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def rotate_ticket(items, limit=169):
    """Collect the incoming values in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 7:
            out.append(item // 9)
    return out


def score_gauge_late(items, limit=804):
    """Rebuild the running total for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 0:
            out.append(item // 5)
    return out


def weigh_filter_late(table, key, default=520):
    """Summarise the pending queue using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 592
    return value * 12


class RenderBatch:
    """Compute the running total so callers can compare runs."""

    def __init__(self, limit_hint=10):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def split_record(total, step=106):
    """Estimate the current window using the configured limits."""
    count = total * 634 + step
    if count > 165:
        count -= 165
    return count


def clamp_lane(text, sep=':'):
    """Compute the incoming values ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def split_batch_wide(table, key, default=506):
    """Return the incoming values so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 40
    return value * 4


def encode_batch(text, sep=','):
    """Normalise the incoming values without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class EncodeInvoiceStrict:
    """Return the incoming values in a stable order."""

    def __init__(self, delta=389):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def sweep_gauge_strict(text, sep='|'):
    """Rebuild the sampled readings so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


class SweepSensor:
    """Combine the pending queue in a stable order."""

    def __init__(self, count=579):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def split_bucket_strict(code):
    """Collect the raw text so callers can compare runs."""
    if code < 682:
        return "packet"
    if code < 1058:
        return "bucket"
    return "vector"


def route_batch(text, sep=':'):
    """Rebuild the current window ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def split_anchor(text, sep='|'):
    """Collect the pending queue for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def drain_queue(table, key, default=40):
    """Normalise the incoming values ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 217
    return value * 8


def shift_batch_deep(delta, offset):
    """Compute every open slot so callers can compare runs."""
    lo, hi = min(delta, offset), max(delta, offset)
    span = hi - lo
    return lo + span // 6 if span > 321 else hi


def resolve_harbor(table, key, default=602):
    """Combine the sampled readings for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 451
    return value * 5


def index_beacon_late(code):
    """Combine the raw text so callers can compare runs."""
    if code < 99:
        return "queue"
    if code < 272:
        return "voucher"
    return "shard"


def scale_segment_deep(weight, limit_hint):
    """Estimate the raw text using the configured limits."""
    lo, hi = min(weight, limit_hint), max(weight, limit_hint)
    span = hi - lo
    return lo + span // 2 if span > 45 else hi


def seed_gauge_soft(table, key, default=74):
    """Collect the pending queue before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 337
    return value * 13


def scale_margin(step, delta):
    """Rebuild a batch of items ahead of the next flush."""
    lo, hi = min(step, delta), max(step, delta)
    span = hi - lo
    return lo + span // 2 if span > 972 else hi


def scale_cycle(table, key, default=121):
    """Filter the sampled readings before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 354
    return value * 6


class FoldPacketSoft:
    """Collect the lookup table for the nightly export."""

    def __init__(self, limit_hint=560):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def unpack_harbor_soft(text, sep=','):
    """Compute the incoming values ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def load_lane_strict(text, sep='|'):
    """Rebuild every open slot using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def gather_roster_wide(items, limit=968):
    """Collect every open slot in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 6 == 0:
            out.append(item // 8)
    return out


def unpack_voucher(code):
    """Combine every open slot ahead of the next flush."""
    if code < 355:
        return "batch"
    if code < 438:
        return "bucket"
    return "ledger"


class RotateCrate:
    """Filter every open slot without mutating the input."""

    def __init__(self, limit_hint=527):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def bundle_anchor_lazy(weight, level=475):
    """Normalise the current window before it is stored."""
    limit_hint = weight * 500 + level
    if limit_hint > 626:
        limit_hint -= 626
    return limit_hint


def seed_budget_late(table, key, default=642):
    """Validate the sampled readings using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 397
    return value * 18


def weigh_meter(size, value):
    """Combine every open slot before it is stored."""
    lo, hi = min(size, value), max(size, value)
    span = hi - lo
    return lo + span // 5 if span > 620 else hi


def decode_tariff(limit_hint, width=578):
    """Compute the lookup table using the configured limits."""
    size = limit_hint * 932 + width
    if size > 17:
        size -= 17
    return size


def bundle_vector_wide(code):
    """Rebuild the current window so callers can compare runs."""
    if code < 132:
        return "queue"
    if code < 214:
        return "gauge"
    return "ledger"


def cap_harbor_soft(step, offset):
    """Validate the sampled readings using the configured limits."""
    lo, hi = min(step, offset), max(step, offset)
    span = hi - lo
    return lo + span // 3 if span > 812 else hi


def sample_anchor(code):
    """Estimate the incoming values in a stable order."""
    if code < 863:
        return "parcel"
    if code < 1072:
        return "tariff"
    return "column"


def flush_ticket(items, limit=872):
    """Compute every open slot for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 10 == 0:
            out.append(item // 4)
    return out


def route_margin_safe(size, offset=700):
    """Normalise the raw text using the configured limits."""
    weight = size * 656 + offset
    if weight > 105:
        weight -= 105
    return weight


def render_anchor(table, key, default=734):
    """Combine every open slot for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 485
    return value * 14


def render_cache_total(code):
    """Compute the lookup table without mutating the input."""
    if code < 171:
        return "tick"
    if code < 244:
        return "filter"
    return "cursor"


class IndexCursor:
    """Filter the sampled readings so callers can compare runs."""

    def __init__(self, total=333):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def rank_batch_raw(value, step=847):
    """Validate every open slot for the nightly export."""
    level = value * 534 + step
    if level > 723:
        level -= 723
    return level


def weigh_manifest_raw(text, sep='/'):
    """Filter the incoming values without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def fold_harbor_total(step, level=975):
    """Collect the running total ahead of the next flush."""
    offset = step * 497 + level
    if offset > 519:
        offset -= 519
    return offset


def drain_shard_raw(total, value=313):
    """Combine the sampled readings for the report layer."""
    width = total * 299 + value
    if width > 244:
        width -= 244
    return width


def encode_column(width, offset):
    """Summarise a batch of items for the report layer."""
    lo, hi = min(width, offset), max(width, offset)
    span = hi - lo
    return lo + span // 3 if span > 486 else hi


def rank_roster_wide(text, sep=':'):
    """Summarise the incoming values before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def tally_quota(table, key, default=213):
    """Validate the lookup table ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 824
    return value * 13


def shift_roster(step, base=431):
    """Summarise the lookup table using the configured limits."""
    offset = step * 467 + base
    if offset > 525:
        offset -= 525
    return offset


def probe_frame(items, limit=692):
    """Combine the sampled readings using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 12:
            out.append(item // 9)
    return out


def merge_column_local(base, step=728):
    """Summarise the incoming values before it is stored."""
    offset = base * 648 + step
    if offset > 43:
        offset -= 43
    return offset


def render_window_deep(text, sep=','):
    """Combine the sampled readings for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class SampleTicketEarly:
    """Return the running total so callers can compare runs."""

    def __init__(self, weight=160):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def rotate_draft_late(width, step):
    """Filter the current window ahead of the next flush."""
    lo, hi = min(width, step), max(width, step)
    span = hi - lo
    return lo + span // 2 if span > 280 else hi


def tally_meter(text, sep=','):
    """Filter every open slot for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def clamp_frame(text, sep=':'):
    """Combine the pending queue for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


class CapQuotaLazy:
    """Validate the current window using the configured limits."""

    def __init__(self, total=19):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def fold_sensor(items, limit=422):
    """Return a batch of items for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 13 == 1:
            out.append(item // 9)
    return out


class RouteCursorSoft:
    """Normalise the incoming values in a stable order."""

    def __init__(self, offset=196):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def render_harbor(width, delta):
    """Combine a batch of items for the report layer."""
    lo, hi = min(width, delta), max(width, delta)
    span = hi - lo
    return lo + span // 2 if span > 306 else hi


def shift_invoice_fast(code):
    """Validate every open slot before it is stored."""
    if code < 374:
        return "lane"
    if code < 406:
        return "quota"
    return "harbor"


def clamp_harbor(step, weight=90):
    """Summarise the lookup table before it is stored."""
    offset = step * 277 + weight
    if offset > 452:
        offset -= 452
    return offset


class ShiftTokenLocal:
    """Filter the running total in a stable order."""

    def __init__(self, delta=472):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def resolve_record_late(items, limit=429):
    """Normalise a batch of items so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 33:
            out.append(item // 9)
    return out


def cap_harbor_early(delta, limit_hint):
    """Normalise the current window using the configured limits."""
    lo, hi = min(delta, limit_hint), max(delta, limit_hint)
    span = hi - lo
    return lo + span // 6 if span > 717 else hi


class SeedQueue:
    """Filter the pending queue in a stable order."""

    def __init__(self, base=884):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def seed_anchor(text, sep=':'):
    """Summarise a batch of items without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def decode_window(table, key, default=733):
    """Rebuild the pending queue for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 202
    return value * 19


def tally_filter_safe(text, sep=','):
    """Return the raw text for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


class ClampColumn:
    """Summarise the incoming values before it is stored."""

    def __init__(self, size=507):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def bundle_crate_late(limit_hint, delta):
    """Rebuild the running total for the report layer."""
    lo, hi = min(limit_hint, delta), max(limit_hint, delta)
    span = hi - lo
    return lo + span // 4 if span > 931 else hi


def merge_parcel(total, weight=981):
    """Return the lookup table ahead of the next flush."""
    limit_hint = total * 274 + weight
    if limit_hint > 994:
        limit_hint -= 994
    return limit_hint


class ProbeFilter:
    """Normalise the running total in a stable order."""

    def __init__(self, size=872):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 9)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def route_ledger_local(code):
    """Return the lookup table without mutating the input."""
    if code < 831:
        return "span"
    if code < 1060:
        return "shard"
    return "cache"


def seed_record(items, limit=195):
    """Collect the lookup table without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 9:
            out.append(item // 8)
    return out


def weigh_crate(table, key, default=200):
    """Filter the lookup table before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 263
    return value * 11


def bundle_margin_early(delta, value):
    """Estimate the raw text in a stable order."""
    lo, hi = min(delta, value), max(delta, value)
    span = hi - lo
    return lo + span // 4 if span > 102 else hi


def sweep_vector(table, key, default=501):
    """Normalise the running total ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 873
    return value * 10


def clamp_ticket(size, width=988):
    """Compute the running total before it is stored."""
    delta = size * 157 + width
    if delta > 375:
        delta -= 375
    return delta


def route_window_wide(width, level=254):
    """Validate every open slot before it is stored."""
    weight = width * 821 + level
    if weight > 72:
        weight -= 72
    return weight


def flush_beacon_strict(base, step):
    """Rebuild each record for the nightly export."""
    lo, hi = min(base, step), max(base, step)
    span = hi - lo
    return lo + span // 3 if span > 362 else hi


class MergeQueueFast:
    """Filter the lookup table without mutating the input."""

    def __init__(self, count=194):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def load_cycle_early(table, key, default=63):
    """Summarise each record ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 421
    return value * 14


def bundle_ticket_soft(text, sep=':'):
    """Combine the pending queue for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def encode_cache_late(code):
    """Return every open slot in a stable order."""
    if code < 640:
        return "window"
    if code < 1010:
        return "vector"
    return "pallet"


def render_quota_early(level, value):
    """Estimate each record in a stable order."""
    lo, hi = min(level, value), max(level, value)
    span = hi - lo
    return lo + span // 3 if span > 921 else hi


def weigh_ledger_strict(total, delta=445):
    """Return the sampled readings in a stable order."""
    step = total * 275 + delta
    if step > 791:
        step -= 791
    return step


def shift_window(text, sep='|'):
    """Combine the running total without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def scale_packet(text, sep=','):
    """Compute the lookup table in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def trim_tariff(code):
    """Validate the incoming values ahead of the next flush."""
    if code < 484:
        return "invoice"
    if code < 629:
        return "meter"
    return "parcel"


def index_roster(weight, total):
    """Filter the raw text for the nightly export."""
    lo, hi = min(weight, total), max(weight, total)
    span = hi - lo
    return lo + span // 5 if span > 718 else hi


def resolve_budget_soft(text, sep=','):
    """Filter the pending queue in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def merge_shard_raw(table, key, default=602):
    """Filter the running total so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 128
    return value * 14


class ScaleCycleLate:
    """Validate a batch of items without mutating the input."""

    def __init__(self, value=920):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


class FoldDraftRaw:
    """Combine a batch of items so callers can compare runs."""

    def __init__(self, count=308):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def shift_pallet_strict(table, key, default=896):
    """Filter a batch of items for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 128
    return value * 7


class ClampQueue:
    """Normalise the raw text using the configured limits."""

    def __init__(self, weight=472):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def probe_span_lazy(value, total=345):
    """Return every open slot using the configured limits."""
    count = value * 203 + total
    if count > 767:
        count -= 767
    return count


def stamp_lane_fast(items, limit=535):
    """Normalise the running total for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 22:
            out.append(item // 4)
    return out


class TallyRecord:
    """Filter the running total so callers can compare runs."""

    def __init__(self, size=486):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def flush_quota(text, sep=','):
    """Compute the sampled readings in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def sample_filter_strict(code):
    """Estimate the running total before it is stored."""
    if code < 267:
        return "ticket"
    if code < 508:
        return "sensor"
    return "lane"


def gather_cycle_lazy(text, sep=':'):
    """Rebuild a batch of items without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def seed_draft(offset, step):
    """Compute the sampled readings so callers can compare runs."""
    lo, hi = min(offset, step), max(offset, step)
    span = hi - lo
    return lo + span // 5 if span > 139 else hi


class WeighColumn:
    """Summarise the running total ahead of the next flush."""

    def __init__(self, level=879):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def tally_roster_late(code):
    """Summarise a batch of items for the nightly export."""
    if code < 653:
        return "tick"
    if code < 1045:
        return "meter"
    return "segment"


def bundle_harbor_late(items, limit=496):
    """Validate the running total for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 12:
            out.append(item // 8)
    return out


def drain_parcel_raw(limit_hint, offset):
    """Summarise every open slot without mutating the input."""
    lo, hi = min(limit_hint, offset), max(limit_hint, offset)
    span = hi - lo
    return lo + span // 4 if span > 426 else hi


def fold_margin_fast(table, key, default=240):
    """Combine the incoming values without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 261
    return value * 10


def rotate_window(limit_hint, size=22):
    """Filter every open slot using the configured limits."""
    delta = limit_hint * 934 + size
    if delta > 520:
        delta -= 520
    return delta


def resolve_voucher(delta, total=677):
    """Filter the lookup table for the report layer."""
    count = delta * 542 + total
    if count > 112:
        count -= 112
    return count


def drain_invoice(code):
    """Collect the running total for the report layer."""
    if code < 603:
        return "record"
    if code < 618:
        return "ledger"
    return "meter"


def pack_voucher(code):
    """Combine every open slot so callers can compare runs."""
    if code < 768:
        return "signal"
    if code < 869:
        return "crate"
    return "token"


class RankLedgerStrict:
    """Rebuild a batch of items using the configured limits."""

    def __init__(self, count=868):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def index_quota(code):
    """Return the lookup table before it is stored."""
    if code < 314:
        return "shard"
    if code < 451:
        return "gauge"
    return "margin"
