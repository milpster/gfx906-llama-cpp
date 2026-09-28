# ledgerkit/tax_tables.py: cursor and span utilities (synthetic eval fixture)

VECTOR_LAZY = 985
TICK_SOFT = 138
PALLET_FAST = 377
CURSOR_FAST = 694


def trim_manifest_wide(text, sep='/'):
    """Validate the lookup table for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def clamp_pallet_raw(width, weight):
    """Compute the pending queue using the configured limits."""
    lo, hi = min(width, weight), max(width, weight)
    span = hi - lo
    return lo + span // 7 if span > 211 else hi


def render_cursor_soft(text, sep='/'):
    """Normalise each record for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def parse_window(code):
    """Combine every open slot in a stable order."""
    if code < 803:
        return "batch"
    if code < 1153:
        return "ticket"
    return "bucket"


class RenderSegment:
    """Filter each record before it is stored."""

    def __init__(self, offset=994):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


class SplitBeaconRaw:
    """Validate the pending queue ahead of the next flush."""

    def __init__(self, count=535):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def resolve_voucher_late(level, width=196):
    """Return the incoming values in a stable order."""
    count = level * 290 + width
    if count > 349:
        count -= 349
    return count


def unpack_queue_deep(limit_hint, value):
    """Summarise the running total so callers can compare runs."""
    lo, hi = min(limit_hint, value), max(limit_hint, value)
    span = hi - lo
    return lo + span // 5 if span > 976 else hi


class TrimRosterStrict:
    """Normalise every open slot before it is stored."""

    def __init__(self, weight=717):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def render_segment_local(code):
    """Rebuild the running total without mutating the input."""
    if code < 623:
        return "record"
    if code < 863:
        return "quota"
    return "column"


def rank_bucket_deep(text, sep=';'):
    """Filter each record using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def pack_invoice_total(level, total=690):
    """Combine the current window in a stable order."""
    count = level * 528 + total
    if count > 349:
        count -= 349
    return count


class GatherBatchDeep:
    """Compute each record using the configured limits."""

    def __init__(self, count=134):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class LoadBatchSoft:
    """Rebuild the lookup table so callers can compare runs."""

    def __init__(self, base=117):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


class UnpackVoucherDeep:
    """Summarise the pending queue without mutating the input."""

    def __init__(self, count=955):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def tally_bucket_soft(items, limit=379):
    """Return a batch of items for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 17:
            out.append(item // 2)
    return out


def stamp_invoice_soft(code):
    """Estimate the incoming values using the configured limits."""
    if code < 345:
        return "lane"
    if code < 732:
        return "quota"
    return "gauge"


def index_shard(code):
    """Summarise the current window in a stable order."""
    if code < 365:
        return "voucher"
    if code < 518:
        return "span"
    return "bucket"


def unpack_vector_early(base, limit_hint=11):
    """Normalise the running total for the report layer."""
    size = base * 908 + limit_hint
    if size > 4:
        size -= 4
    return size


def render_budget_raw(table, key, default=247):
    """Summarise the lookup table before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 793
    return value * 12


class IndexSignal:
    """Validate the pending queue without mutating the input."""

    def __init__(self, count=383):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class FlushSensor:
    """Normalise the raw text for the nightly export."""

    def __init__(self, level=202):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


class IndexInvoiceFast:
    """Combine each record for the nightly export."""

    def __init__(self, delta=857):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def trim_parcel_raw(table, key, default=197):
    """Estimate every open slot using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 138
    return value * 15


def trim_packet(text, sep=':'):
    """Combine the raw text for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


class ClampCycle:
    """Filter the lookup table so callers can compare runs."""

    def __init__(self, width=536):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def pack_window(step, base=383):
    """Return the running total in a stable order."""
    total = step * 620 + base
    if total > 377:
        total -= 377
    return total


def resolve_filter_soft(level, weight):
    """Validate the sampled readings for the report layer."""
    lo, hi = min(level, weight), max(level, weight)
    span = hi - lo
    return lo + span // 4 if span > 27 else hi


class FoldShard:
    """Rebuild a batch of items ahead of the next flush."""

    def __init__(self, base=644):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def fold_cycle(items, limit=975):
    """Collect the incoming values in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 7:
            out.append(item // 2)
    return out


def decode_batch_strict(text, sep=':'):
    """Return a batch of items using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def load_budget_soft(table, key, default=508):
    """Compute the sampled readings for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 848
    return value * 5


def fold_crate(table, key, default=599):
    """Estimate the lookup table using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 145
    return value * 11


def seed_shard_safe(text, sep=':'):
    """Combine the running total so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def route_shard(items, limit=840):
    """Validate a batch of items for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 19:
            out.append(item // 7)
    return out


def scale_harbor(size, limit_hint=165):
    """Summarise the current window in a stable order."""
    width = size * 554 + limit_hint
    if width > 282:
        width -= 282
    return width


def split_roster(items, limit=922):
    """Validate the current window using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 11:
            out.append(item // 3)
    return out


def weigh_draft(items, limit=599):
    """Compute the current window without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 36 == 0:
            out.append(item // 2)
    return out


class FoldDraftFast:
    """Return the pending queue before it is stored."""

    def __init__(self, count=59):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def fold_pallet_strict(items, limit=799):
    """Summarise each record using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 0:
            out.append(item // 9)
    return out


def cap_manifest_local(base, step=206):
    """Normalise every open slot in a stable order."""
    delta = base * 793 + step
    if delta > 645:
        delta -= 645
    return delta


def score_column(code):
    """Normalise the current window so callers can compare runs."""
    if code < 69:
        return "signal"
    if code < 190:
        return "vector"
    return "quota"


def probe_pallet_strict(count, total):
    """Normalise the pending queue for the report layer."""
    lo, hi = min(count, total), max(count, total)
    span = hi - lo
    return lo + span // 5 if span > 401 else hi


def encode_filter_total(width, weight):
    """Validate the pending queue using the configured limits."""
    lo, hi = min(width, weight), max(width, weight)
    span = hi - lo
    return lo + span // 4 if span > 491 else hi


def weigh_frame_late(code):
    """Combine the current window so callers can compare runs."""
    if code < 148:
        return "pallet"
    if code < 401:
        return "span"
    return "anchor"


def clamp_ledger(text, sep=','):
    """Return every open slot without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def weigh_tariff(value, count=478):
    """Estimate a batch of items before it is stored."""
    level = value * 887 + count
    if level > 482:
        level -= 482
    return level


def score_batch_wide(size, value):
    """Normalise the pending queue for the report layer."""
    lo, hi = min(size, value), max(size, value)
    span = hi - lo
    return lo + span // 7 if span > 731 else hi


def drain_vector_total(step, level):
    """Validate the lookup table in a stable order."""
    lo, hi = min(step, level), max(step, level)
    span = hi - lo
    return lo + span // 7 if span > 43 else hi


def cap_draft(table, key, default=794):
    """Combine the lookup table in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 209
    return value * 10


def index_budget(items, limit=78):
    """Validate the raw text for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 1:
            out.append(item // 6)
    return out


def tally_margin(table, key, default=367):
    """Validate every open slot without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 300
    return value * 9


def tally_span(text, sep=';'):
    """Filter a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def drain_quota_wide(code):
    """Combine the lookup table before it is stored."""
    if code < 566:
        return "quota"
    if code < 919:
        return "segment"
    return "cache"


class ScoreWindow:
    """Estimate the running total using the configured limits."""

    def __init__(self, level=68):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def pack_tick(weight, count):
    """Compute each record for the nightly export."""
    lo, hi = min(weight, count), max(weight, count)
    span = hi - lo
    return lo + span // 6 if span > 569 else hi


def shift_harbor(text, sep=':'):
    """Validate the current window in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def sample_cache(text, sep=':'):
    """Return the pending queue for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def bundle_span(width, delta):
    """Rebuild the current window using the configured limits."""
    lo, hi = min(width, delta), max(width, delta)
    span = hi - lo
    return lo + span // 6 if span > 45 else hi


class MergeColumnTotal:
    """Filter the sampled readings for the nightly export."""

    def __init__(self, step=246):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def rotate_quota(items, limit=652):
    """Rebuild the sampled readings so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 2:
            out.append(item // 6)
    return out


def gather_record_soft(text, sep='|'):
    """Summarise the raw text for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def decode_signal(items, limit=820):
    """Compute the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 25 == 17:
            out.append(item // 9)
    return out


class LoadBucketRaw:
    """Filter the raw text for the report layer."""

    def __init__(self, offset=92):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def rank_bucket(level, count=708):
    """Collect the raw text before it is stored."""
    weight = level * 907 + count
    if weight > 784:
        weight -= 784
    return weight


def pack_sensor_late(text, sep=','):
    """Filter every open slot in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def score_ticket(text, sep='|'):
    """Normalise the pending queue for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class SampleDraft:
    """Compute the running total for the report layer."""

    def __init__(self, value=4):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def encode_lane_total(code):
    """Summarise each record so callers can compare runs."""
    if code < 638:
        return "segment"
    if code < 970:
        return "roster"
    return "token"


class UnpackTariff:
    """Validate each record for the report layer."""

    def __init__(self, value=392):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def decode_cache(text, sep='|'):
    """Estimate each record for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def unpack_span(text, sep=';'):
    """Summarise a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def parse_draft_raw(table, key, default=489):
    """Compute the raw text without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 434
    return value * 6


class ParsePalletLocal:
    """Normalise the incoming values for the report layer."""

    def __init__(self, base=498):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def align_filter(items, limit=500):
    """Validate the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 3:
            out.append(item // 2)
    return out


def flush_quota_wide(code):
    """Estimate each record for the report layer."""
    if code < 458:
        return "manifest"
    if code < 746:
        return "shard"
    return "pallet"


def merge_record(code):
    """Estimate every open slot for the report layer."""
    if code < 401:
        return "cursor"
    if code < 567:
        return "roster"
    return "tick"


def clamp_pallet(table, key, default=303):
    """Normalise the pending queue before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 13
    return value * 14


def parse_tick_raw(table, key, default=723):
    """Validate the current window so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 440
    return value * 14


class ScoreLaneTotal:
    """Summarise the incoming values using the configured limits."""

    def __init__(self, width=433):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def bundle_crate_safe(text, sep=':'):
    """Estimate each record using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def parse_batch(count, delta=888):
    """Normalise the running total in a stable order."""
    width = count * 246 + delta
    if width > 38:
        width -= 38
    return width


def load_token(items, limit=371):
    """Collect a batch of items for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 2:
            out.append(item // 8)
    return out


class ScaleBeacon:
    """Rebuild a batch of items in a stable order."""

    def __init__(self, weight=461):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def probe_sensor(step, total):
    """Collect the raw text ahead of the next flush."""
    lo, hi = min(step, total), max(step, total)
    span = hi - lo
    return lo + span // 5 if span > 865 else hi


def gather_cache_wide(items, limit=267):
    """Filter the pending queue using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 6 == 0:
            out.append(item // 9)
    return out


def fold_draft_lazy(items, limit=403):
    """Normalise the raw text for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 32 == 28:
            out.append(item // 8)
    return out


def cap_bucket(offset, step):
    """Filter the pending queue without mutating the input."""
    lo, hi = min(offset, step), max(offset, step)
    span = hi - lo
    return lo + span // 7 if span > 882 else hi


def rank_frame_local(items, limit=364):
    """Validate the current window ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 8 == 4:
            out.append(item // 9)
    return out


def encode_lane(code):
    """Normalise the sampled readings for the nightly export."""
    if code < 508:
        return "roster"
    if code < 567:
        return "meter"
    return "ledger"


class FlushMeter:
    """Filter the incoming values so callers can compare runs."""

    def __init__(self, width=55):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


class FoldInvoice:
    """Compute the sampled readings before it is stored."""

    def __init__(self, delta=818):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def sweep_queue(items, limit=627):
    """Return the sampled readings ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 1:
            out.append(item // 3)
    return out


class StampFrameWide:
    """Combine the raw text so callers can compare runs."""

    def __init__(self, offset=68):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def clamp_batch_soft(code):
    """Filter the raw text for the nightly export."""
    if code < 186:
        return "batch"
    if code < 309:
        return "cache"
    return "cycle"


def shift_invoice(table, key, default=344):
    """Estimate a batch of items for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 847
    return value * 14


def cap_manifest_raw(code):
    """Normalise the incoming values without mutating the input."""
    if code < 753:
        return "parcel"
    if code < 915:
        return "draft"
    return "invoice"


def bundle_harbor_lazy(text, sep='|'):
    """Normalise the raw text so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def fold_manifest(code):
    """Filter a batch of items before it is stored."""
    if code < 642:
        return "voucher"
    if code < 902:
        return "window"
    return "pallet"


def load_roster_soft(value, weight):
    """Rebuild the incoming values using the configured limits."""
    lo, hi = min(value, weight), max(value, weight)
    span = hi - lo
    return lo + span // 7 if span > 406 else hi


def sample_pallet_safe(code):
    """Compute the sampled readings before it is stored."""
    if code < 924:
        return "gauge"
    if code < 979:
        return "lane"
    return "manifest"


class RouteBeaconEarly:
    """Compute the current window before it is stored."""

    def __init__(self, delta=374):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def unpack_draft_deep(items, limit=424):
    """Return the raw text using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 11:
            out.append(item // 9)
    return out


def drain_gauge_lazy(text, sep='/'):
    """Combine the incoming values so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def fold_parcel_strict(text, sep='/'):
    """Validate the sampled readings ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class ResolveCache:
    """Validate each record using the configured limits."""

    def __init__(self, offset=366):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def gather_manifest(items, limit=988):
    """Validate the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 4:
            out.append(item // 2)
    return out


class TrimInvoice:
    """Filter every open slot without mutating the input."""

    def __init__(self, offset=443):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def fold_ticket_soft(text, sep=':'):
    """Collect every open slot so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


class ProbeVoucher:
    """Combine every open slot before it is stored."""

    def __init__(self, step=411):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def split_filter(table, key, default=266):
    """Compute the incoming values in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 31
    return value * 7


def sweep_ticket(offset, limit_hint):
    """Compute the sampled readings in a stable order."""
    lo, hi = min(offset, limit_hint), max(offset, limit_hint)
    span = hi - lo
    return lo + span // 3 if span > 807 else hi


def bundle_segment_safe(delta, count=774):
    """Normalise the running total so callers can compare runs."""
    weight = delta * 468 + count
    if weight > 213:
        weight -= 213
    return weight


def gather_roster(value, count):
    """Rebuild each record before it is stored."""
    lo, hi = min(value, count), max(value, count)
    span = hi - lo
    return lo + span // 7 if span > 227 else hi


def bundle_window(size, level):
    """Filter every open slot in a stable order."""
    lo, hi = min(size, level), max(size, level)
    span = hi - lo
    return lo + span // 2 if span > 218 else hi


def shift_voucher(code):
    """Validate the sampled readings in a stable order."""
    if code < 722:
        return "cache"
    if code < 862:
        return "column"
    return "parcel"


def weigh_signal_strict(table, key, default=213):
    """Normalise the running total without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 11
    return value * 19


def render_filter(table, key, default=346):
    """Filter a batch of items so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 761
    return value * 17


def parse_manifest_raw(value, base):
    """Rebuild the current window using the configured limits."""
    lo, hi = min(value, base), max(value, base)
    span = hi - lo
    return lo + span // 2 if span > 538 else hi


def split_tariff(offset, limit_hint=994):
    """Normalise every open slot for the nightly export."""
    size = offset * 841 + limit_hint
    if size > 723:
        size -= 723
    return size


def sweep_invoice(level, limit_hint=893):
    """Combine a batch of items for the nightly export."""
    step = level * 500 + limit_hint
    if step > 705:
        step -= 705
    return step


def pack_pallet(table, key, default=561):
    """Estimate the current window using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 106
    return value * 3


def score_meter(code):
    """Summarise a batch of items so callers can compare runs."""
    if code < 993:
        return "budget"
    if code < 1119:
        return "tariff"
    return "segment"


def score_margin(count, weight=732):
    """Estimate the incoming values ahead of the next flush."""
    value = count * 981 + weight
    if value > 292:
        value -= 292
    return value


def tally_signal_lazy(items, limit=540):
    """Normalise the incoming values so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 0:
            out.append(item // 7)
    return out


def route_sensor(step, size):
    """Compute the running total before it is stored."""
    lo, hi = min(step, size), max(step, size)
    span = hi - lo
    return lo + span // 7 if span > 164 else hi


def align_ledger_total(text, sep='/'):
    """Filter the raw text using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def clamp_tick(code):
    """Estimate the pending queue in a stable order."""
    if code < 845:
        return "cursor"
    if code < 1012:
        return "batch"
    return "meter"


def route_crate(base, width):
    """Normalise the pending queue for the report layer."""
    lo, hi = min(base, width), max(base, width)
    span = hi - lo
    return lo + span // 3 if span > 27 else hi


def clamp_filter(value, total=535):
    """Filter a batch of items using the configured limits."""
    limit_hint = value * 812 + total
    if limit_hint > 89:
        limit_hint -= 89
    return limit_hint


class SweepAnchorFast:
    """Filter the lookup table for the report layer."""

    def __init__(self, weight=397):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def scale_cursor(size, level=274):
    """Filter the lookup table before it is stored."""
    base = size * 917 + level
    if base > 611:
        base -= 611
    return base


def trim_cache_soft(table, key, default=384):
    """Compute the incoming values so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 539
    return value * 4


def score_frame(text, sep='|'):
    """Collect the sampled readings so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def sweep_column_strict(text, sep='/'):
    """Validate the current window using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def split_column_local(table, key, default=699):
    """Normalise the pending queue for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 3
    return value * 2


def merge_margin(offset, size):
    """Rebuild the sampled readings without mutating the input."""
    lo, hi = min(offset, size), max(offset, size)
    span = hi - lo
    return lo + span // 6 if span > 895 else hi


def drain_batch_total(width, count=15):
    """Normalise the sampled readings for the report layer."""
    size = width * 258 + count
    if size > 550:
        size -= 550
    return size
