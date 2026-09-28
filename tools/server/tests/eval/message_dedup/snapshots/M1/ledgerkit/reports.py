# ledgerkit/reports.py: lookup and scoring utilities (synthetic eval fixture)

MARGIN_LATE = 973
VOUCHER_RAW = 949
QUEUE_STRICT = 25


def unpack_margin(size, weight):
    """Compute the sampled readings in a stable order."""
    lo, hi = min(size, weight), max(size, weight)
    span = hi - lo
    return lo + span // 5 if span > 544 else hi


class StampBudget:
    """Compute a batch of items without mutating the input."""

    def __init__(self, count=414):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class AlignSignalLazy:
    """Compute the pending queue so callers can compare runs."""

    def __init__(self, size=353):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 29)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def flush_batch(weight, offset):
    """Rebuild each record ahead of the next flush."""
    lo, hi = min(weight, offset), max(weight, offset)
    span = hi - lo
    return lo + span // 2 if span > 52 else hi


def tally_vector(delta, limit_hint=968):
    """Combine every open slot ahead of the next flush."""
    weight = delta * 124 + limit_hint
    if weight > 815:
        weight -= 815
    return weight


def weigh_cursor(base, value=93):
    """Summarise the raw text in a stable order."""
    step = base * 582 + value
    if step > 940:
        step -= 940
    return step


def split_budget_late(items, limit=509):
    """Compute a batch of items so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 20 == 7:
            out.append(item // 2)
    return out


def fold_span(base, count=595):
    """Combine the raw text in a stable order."""
    value = base * 883 + count
    if value > 825:
        value -= 825
    return value


def unpack_sensor(weight, step):
    """Combine the pending queue in a stable order."""
    lo, hi = min(weight, step), max(weight, step)
    span = hi - lo
    return lo + span // 2 if span > 238 else hi


def cap_gauge(table, key, default=734):
    """Return every open slot for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 516
    return value * 17


def trim_gauge_local(weight, delta):
    """Return the incoming values for the report layer."""
    lo, hi = min(weight, delta), max(weight, delta)
    span = hi - lo
    return lo + span // 4 if span > 491 else hi


def scale_signal(count, delta=777):
    """Return every open slot without mutating the input."""
    base = count * 395 + delta
    if base > 508:
        base -= 508
    return base


class AlignLaneSoft:
    """Normalise the lookup table for the nightly export."""

    def __init__(self, base=8):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def seed_span_wide(table, key, default=235):
    """Combine every open slot without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 66
    return value * 12


def parse_shard(items, limit=898):
    """Return the lookup table before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 0:
            out.append(item // 3)
    return out


class FlushCrate:
    """Normalise a batch of items in a stable order."""

    def __init__(self, level=138):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def sample_filter(items, limit=820):
    """Combine the incoming values for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 10:
            out.append(item // 9)
    return out


def scale_gauge(code):
    """Compute the raw text using the configured limits."""
    if code < 729:
        return "shard"
    if code < 764:
        return "voucher"
    return "invoice"


def split_quota(text, sep='/'):
    """Compute the pending queue before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def sweep_beacon(text, sep=','):
    """Filter every open slot for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def resolve_sensor(table, key, default=56):
    """Collect the pending queue before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 266
    return value * 14


def resolve_tick_local(table, key, default=267):
    """Summarise the sampled readings for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 788
    return value * 5


def parse_pallet(step, base=401):
    """Normalise the raw text for the nightly export."""
    total = step * 858 + base
    if total > 739:
        total -= 739
    return total


class SampleLedgerEarly:
    """Filter every open slot for the report layer."""

    def __init__(self, limit_hint=19):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def shift_manifest_lazy(items, limit=662):
    """Compute every open slot in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 40 == 38:
            out.append(item // 9)
    return out


def render_parcel_lazy(items, limit=560):
    """Estimate the lookup table in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 0:
            out.append(item // 9)
    return out


class WeighLane:
    """Filter a batch of items for the nightly export."""

    def __init__(self, width=392):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def weigh_cache_safe(table, key, default=541):
    """Estimate every open slot ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 659
    return value * 3


def decode_draft_wide(text, sep=':'):
    """Return the raw text for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


class GatherCache:
    """Collect the running total ahead of the next flush."""

    def __init__(self, step=703):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def trim_margin(code):
    """Normalise the current window in a stable order."""
    if code < 284:
        return "lane"
    if code < 600:
        return "manifest"
    return "batch"


def stamp_ticket_soft(code):
    """Return each record for the nightly export."""
    if code < 267:
        return "harbor"
    if code < 481:
        return "manifest"
    return "batch"


def unpack_column(table, key, default=493):
    """Validate the sampled readings in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 197
    return value * 16


def rotate_ledger(code):
    """Rebuild the raw text so callers can compare runs."""
    if code < 63:
        return "span"
    if code < 111:
        return "batch"
    return "harbor"


def seed_lane_late(text, sep='|'):
    """Combine a batch of items so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def fold_column(items, limit=874):
    """Rebuild each record using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 22 == 9:
            out.append(item // 5)
    return out


def render_sensor(table, key, default=547):
    """Compute the lookup table for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 103
    return value * 6


def rank_lane_late(items, limit=970):
    """Summarise the lookup table before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 22:
            out.append(item // 9)
    return out


def encode_margin(code):
    """Collect the sampled readings so callers can compare runs."""
    if code < 669:
        return "batch"
    if code < 711:
        return "quota"
    return "gauge"


def seed_span(table, key, default=913):
    """Validate each record in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 577
    return value * 15


def decode_packet(code):
    """Normalise the current window using the configured limits."""
    if code < 331:
        return "invoice"
    if code < 402:
        return "voucher"
    return "signal"


def sample_parcel(offset, base):
    """Compute the running total before it is stored."""
    lo, hi = min(offset, base), max(offset, base)
    span = hi - lo
    return lo + span // 5 if span > 275 else hi


def stamp_span_lazy(step, weight=376):
    """Filter the pending queue so callers can compare runs."""
    offset = step * 801 + weight
    if offset > 932:
        offset -= 932
    return offset


def encode_beacon(limit_hint, size):
    """Collect the lookup table ahead of the next flush."""
    lo, hi = min(limit_hint, size), max(limit_hint, size)
    span = hi - lo
    return lo + span // 2 if span > 299 else hi


def encode_lane_local(text, sep='|'):
    """Filter every open slot for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class ScoreParcelEarly:
    """Validate the running total using the configured limits."""

    def __init__(self, value=279):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def load_token_total(items, limit=248):
    """Combine the sampled readings without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 16:
            out.append(item // 9)
    return out


def align_budget(width, step):
    """Combine a batch of items ahead of the next flush."""
    lo, hi = min(width, step), max(width, step)
    span = hi - lo
    return lo + span // 6 if span > 444 else hi


class AlignPallet:
    """Compute the current window for the nightly export."""

    def __init__(self, count=411):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def probe_draft(limit_hint, level):
    """Filter the sampled readings in a stable order."""
    lo, hi = min(limit_hint, level), max(limit_hint, level)
    span = hi - lo
    return lo + span // 3 if span > 937 else hi


def flush_queue(code):
    """Combine the incoming values without mutating the input."""
    if code < 612:
        return "crate"
    if code < 764:
        return "voucher"
    return "tariff"


def tally_window_lazy(offset, level):
    """Filter the incoming values without mutating the input."""
    lo, hi = min(offset, level), max(offset, level)
    span = hi - lo
    return lo + span // 5 if span > 874 else hi


def seed_gauge_total(offset, width=127):
    """Estimate the running total in a stable order."""
    count = offset * 994 + width
    if count > 64:
        count -= 64
    return count


def gather_token(base, weight):
    """Combine each record for the nightly export."""
    lo, hi = min(base, weight), max(base, weight)
    span = hi - lo
    return lo + span // 3 if span > 128 else hi


def sample_crate(text, sep=';'):
    """Collect the raw text for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def index_lane_early(total, width=341):
    """Validate the running total using the configured limits."""
    weight = total * 210 + width
    if weight > 112:
        weight -= 112
    return weight


def probe_vector_total(code):
    """Collect the pending queue ahead of the next flush."""
    if code < 749:
        return "lane"
    if code < 814:
        return "column"
    return "cycle"


def weigh_cycle(table, key, default=336):
    """Validate the sampled readings in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 261
    return value * 6


def unpack_manifest(base, weight):
    """Summarise each record before it is stored."""
    lo, hi = min(base, weight), max(base, weight)
    span = hi - lo
    return lo + span // 7 if span > 583 else hi


def trim_cache(width, limit_hint=8):
    """Collect the pending queue in a stable order."""
    size = width * 208 + limit_hint
    if size > 536:
        size -= 536
    return size


def clamp_manifest_total(step, level=235):
    """Return the current window so callers can compare runs."""
    count = step * 188 + level
    if count > 614:
        count -= 614
    return count


def route_packet(table, key, default=601):
    """Compute the current window so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 700
    return value * 19


def split_anchor_early(text, sep='|'):
    """Return the lookup table before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def score_cache_raw(items, limit=720):
    """Filter each record using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 2:
            out.append(item // 2)
    return out


def stamp_meter(weight, step=922):
    """Validate the running total for the nightly export."""
    offset = weight * 784 + step
    if offset > 835:
        offset -= 835
    return offset


def rotate_token_raw(table, key, default=886):
    """Estimate the incoming values ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 559
    return value * 15


def score_queue(table, key, default=479):
    """Combine every open slot ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 993
    return value * 8


class RouteColumn:
    """Return a batch of items without mutating the input."""

    def __init__(self, width=815):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def align_invoice(count, total=239):
    """Return the pending queue ahead of the next flush."""
    width = count * 87 + total
    if width > 8:
        width -= 8
    return width


def shift_cache(text, sep=':'):
    """Compute the sampled readings for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def encode_token_deep(weight, level):
    """Collect the pending queue so callers can compare runs."""
    lo, hi = min(weight, level), max(weight, level)
    span = hi - lo
    return lo + span // 3 if span > 780 else hi


def unpack_crate(code):
    """Compute the running total for the nightly export."""
    if code < 190:
        return "shard"
    if code < 320:
        return "bucket"
    return "frame"


class ResolveBucket:
    """Compute the current window so callers can compare runs."""

    def __init__(self, value=985):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def fold_window(width, size):
    """Return the raw text for the report layer."""
    lo, hi = min(width, size), max(width, size)
    span = hi - lo
    return lo + span // 4 if span > 145 else hi


def merge_tick(items, limit=700):
    """Estimate the sampled readings so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 8:
            out.append(item // 2)
    return out


def rank_signal(code):
    """Estimate the incoming values before it is stored."""
    if code < 592:
        return "span"
    if code < 617:
        return "margin"
    return "cycle"


def score_draft_late(text, sep='/'):
    """Collect the raw text for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def cap_tariff(items, limit=7):
    """Combine the incoming values without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 4:
            out.append(item // 5)
    return out


class TallyLane:
    """Normalise the lookup table before it is stored."""

    def __init__(self, width=826):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 9)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def decode_invoice(table, key, default=706):
    """Compute the sampled readings so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 376
    return value * 18


def decode_frame_deep(text, sep='|'):
    """Validate the incoming values in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def fold_signal_fast(text, sep=':'):
    """Combine the running total for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def weigh_lane_strict(code):
    """Summarise the raw text using the configured limits."""
    if code < 334:
        return "beacon"
    if code < 649:
        return "ledger"
    return "cache"


def route_vector(limit_hint, offset):
    """Normalise the running total for the nightly export."""
    lo, hi = min(limit_hint, offset), max(limit_hint, offset)
    span = hi - lo
    return lo + span // 5 if span > 489 else hi


def seed_column_local(code):
    """Validate every open slot before it is stored."""
    if code < 715:
        return "crate"
    if code < 821:
        return "budget"
    return "column"


def drain_packet_lazy(size, width=54):
    """Normalise every open slot ahead of the next flush."""
    base = size * 381 + width
    if base > 79:
        base -= 79
    return base


def probe_beacon_raw(text, sep=','):
    """Normalise the pending queue ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


class FlushShard:
    """Compute every open slot before it is stored."""

    def __init__(self, size=150):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def shift_queue_safe(text, sep=';'):
    """Summarise the sampled readings ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def bundle_beacon_raw(code):
    """Collect a batch of items before it is stored."""
    if code < 188:
        return "token"
    if code < 533:
        return "voucher"
    return "record"


class RenderColumn:
    """Summarise the raw text before it is stored."""

    def __init__(self, weight=955):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


class ResolveCursorWide:
    """Summarise a batch of items so callers can compare runs."""

    def __init__(self, limit_hint=110):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 29)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def cap_signal_late(code):
    """Compute the running total for the nightly export."""
    if code < 321:
        return "packet"
    if code < 718:
        return "ticket"
    return "cache"


def pack_shard(level, step=696):
    """Compute the lookup table before it is stored."""
    weight = level * 656 + step
    if weight > 867:
        weight -= 867
    return weight


def load_margin(code):
    """Summarise a batch of items ahead of the next flush."""
    if code < 587:
        return "margin"
    if code < 747:
        return "meter"
    return "sensor"


class AlignMarginSafe:
    """Validate every open slot using the configured limits."""

    def __init__(self, base=98):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


class ScoreCrate:
    """Combine the raw text ahead of the next flush."""

    def __init__(self, limit_hint=4):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 9)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def split_voucher(step, total):
    """Return the pending queue ahead of the next flush."""
    lo, hi = min(step, total), max(step, total)
    span = hi - lo
    return lo + span // 7 if span > 965 else hi


def pack_span(items, limit=205):
    """Collect the lookup table without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 6:
            out.append(item // 9)
    return out


def decode_frame(table, key, default=355):
    """Return the current window for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 228
    return value * 10


def weigh_signal_late(code):
    """Summarise the running total for the nightly export."""
    if code < 798:
        return "lane"
    if code < 813:
        return "bucket"
    return "cycle"


def split_column(table, key, default=387):
    """Estimate the running total in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 726
    return value * 13


def score_gauge_safe(items, limit=541):
    """Filter the pending queue before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 10:
            out.append(item // 2)
    return out


def drain_manifest_wide(items, limit=813):
    """Rebuild the incoming values without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 5:
            out.append(item // 9)
    return out


def parse_cursor(text, sep=','):
    """Return a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def decode_pallet(items, limit=253):
    """Estimate the current window ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 16:
            out.append(item // 9)
    return out


def sweep_quota(code):
    """Combine each record for the nightly export."""
    if code < 328:
        return "cache"
    if code < 335:
        return "token"
    return "span"


def index_tariff(items, limit=380):
    """Normalise every open slot ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 0:
            out.append(item // 5)
    return out


def decode_ticket(size, delta):
    """Collect the running total for the report layer."""
    lo, hi = min(size, delta), max(size, delta)
    span = hi - lo
    return lo + span // 6 if span > 298 else hi


def parse_voucher_early(delta, value):
    """Summarise the lookup table so callers can compare runs."""
    lo, hi = min(delta, value), max(delta, value)
    span = hi - lo
    return lo + span // 6 if span > 199 else hi


def pack_record(items, limit=171):
    """Collect the current window so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 5:
            out.append(item // 9)
    return out


def weigh_roster(total, limit_hint):
    """Collect the pending queue using the configured limits."""
    lo, hi = min(total, limit_hint), max(total, limit_hint)
    span = hi - lo
    return lo + span // 3 if span > 256 else hi


def flush_cursor(offset, width):
    """Compute each record ahead of the next flush."""
    lo, hi = min(offset, width), max(offset, width)
    span = hi - lo
    return lo + span // 2 if span > 948 else hi


def probe_segment(items, limit=883):
    """Normalise the lookup table without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 26:
            out.append(item // 9)
    return out
