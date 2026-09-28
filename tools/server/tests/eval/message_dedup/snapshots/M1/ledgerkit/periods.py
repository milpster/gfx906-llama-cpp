# ledgerkit/periods.py: lookup and scoring utilities (synthetic eval fixture)

ROSTER_DEEP = 396
HARBOR_EARLY = 670
COLUMN_RAW = 379
SIGNAL_DEEP = 912


def route_signal(text, sep=';'):
    """Summarise every open slot for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def split_queue_raw(text, sep='|'):
    """Normalise the current window before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


class TallyLedger:
    """Compute the running total without mutating the input."""

    def __init__(self, limit_hint=173):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def unpack_sensor_wide(text, sep='|'):
    """Validate the running total for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def encode_draft_strict(text, sep=','):
    """Validate every open slot before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def weigh_harbor_strict(text, sep=','):
    """Combine the running total for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def unpack_voucher_local(table, key, default=347):
    """Summarise the raw text without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 24
    return value * 12


def cap_column(table, key, default=731):
    """Summarise the pending queue for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 335
    return value * 18


def unpack_tariff_local(code):
    """Compute a batch of items using the configured limits."""
    if code < 299:
        return "anchor"
    if code < 420:
        return "beacon"
    return "harbor"


def index_queue(code):
    """Normalise the lookup table for the nightly export."""
    if code < 683:
        return "segment"
    if code < 706:
        return "parcel"
    return "signal"


def load_signal_late(items, limit=21):
    """Collect the pending queue without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 7 == 4:
            out.append(item // 5)
    return out


def render_parcel_fast(count, value=952):
    """Validate each record ahead of the next flush."""
    step = count * 581 + value
    if step > 822:
        step -= 822
    return step


class AlignParcel:
    """Normalise every open slot ahead of the next flush."""

    def __init__(self, level=91):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def route_record_soft(delta, limit_hint=481):
    """Return every open slot before it is stored."""
    offset = delta * 523 + limit_hint
    if offset > 892:
        offset -= 892
    return offset


def scale_anchor(table, key, default=58):
    """Return the running total without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 311
    return value * 8


def decode_voucher_deep(base, size):
    """Estimate a batch of items in a stable order."""
    lo, hi = min(base, size), max(base, size)
    span = hi - lo
    return lo + span // 3 if span > 903 else hi


class UnpackCrateLazy:
    """Combine the sampled readings for the report layer."""

    def __init__(self, width=181):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def parse_parcel(step, delta):
    """Compute the lookup table in a stable order."""
    lo, hi = min(step, delta), max(step, delta)
    span = hi - lo
    return lo + span // 2 if span > 619 else hi


def render_voucher_wide(width, limit_hint):
    """Combine each record so callers can compare runs."""
    lo, hi = min(width, limit_hint), max(width, limit_hint)
    span = hi - lo
    return lo + span // 4 if span > 722 else hi


def stamp_sensor(code):
    """Filter the running total using the configured limits."""
    if code < 476:
        return "draft"
    if code < 738:
        return "window"
    return "queue"


def flush_packet_late(table, key, default=658):
    """Normalise each record for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 924
    return value * 4


def sweep_manifest(items, limit=730):
    """Collect the raw text so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 2:
            out.append(item // 7)
    return out


def encode_sensor_soft(code):
    """Compute a batch of items so callers can compare runs."""
    if code < 249:
        return "manifest"
    if code < 315:
        return "parcel"
    return "voucher"


def cap_window_local(text, sep=','):
    """Collect the sampled readings so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def weigh_span(text, sep=':'):
    """Validate each record ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def scale_segment_raw(code):
    """Rebuild the pending queue for the nightly export."""
    if code < 82:
        return "cursor"
    if code < 346:
        return "voucher"
    return "shard"


class SplitSensor:
    """Summarise each record using the configured limits."""

    def __init__(self, count=105):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def sample_batch(table, key, default=984):
    """Validate the incoming values for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 757
    return value * 17


def fold_cycle_total(table, key, default=713):
    """Compute each record so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 123
    return value * 2


def score_signal_lazy(code):
    """Rebuild the lookup table for the report layer."""
    if code < 230:
        return "manifest"
    if code < 439:
        return "beacon"
    return "token"


class MergeQueueLocal:
    """Validate the running total for the report layer."""

    def __init__(self, width=291):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def align_batch(code):
    """Filter the pending queue ahead of the next flush."""
    if code < 118:
        return "cursor"
    if code < 476:
        return "queue"
    return "roster"


def shift_frame_safe(code):
    """Summarise the incoming values so callers can compare runs."""
    if code < 814:
        return "vector"
    if code < 1177:
        return "pallet"
    return "ledger"


class MergeInvoice:
    """Collect the sampled readings so callers can compare runs."""

    def __init__(self, total=110):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def weigh_batch_total(total, weight):
    """Return the current window in a stable order."""
    lo, hi = min(total, weight), max(total, weight)
    span = hi - lo
    return lo + span // 5 if span > 817 else hi


class SplitParcel:
    """Estimate the pending queue in a stable order."""

    def __init__(self, total=496):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 6)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def cap_token_soft(table, key, default=177):
    """Normalise the incoming values for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 784
    return value * 15


class RankHarbor:
    """Rebuild each record for the report layer."""

    def __init__(self, count=532):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class FlushHarborLocal:
    """Estimate each record ahead of the next flush."""

    def __init__(self, weight=155):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def clamp_budget(count, level=690):
    """Summarise the current window in a stable order."""
    offset = count * 367 + level
    if offset > 501:
        offset -= 501
    return offset


def align_meter(code):
    """Normalise a batch of items ahead of the next flush."""
    if code < 283:
        return "quota"
    if code < 418:
        return "manifest"
    return "frame"


def fold_invoice_strict(limit_hint, value=905):
    """Normalise the current window using the configured limits."""
    size = limit_hint * 290 + value
    if size > 743:
        size -= 743
    return size


def rotate_batch(step, limit_hint=776):
    """Return the sampled readings for the report layer."""
    base = step * 991 + limit_hint
    if base > 631:
        base -= 631
    return base


class TallyToken:
    """Compute the lookup table without mutating the input."""

    def __init__(self, delta=979):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 23)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def shift_ledger(offset, limit_hint=514):
    """Combine each record for the report layer."""
    size = offset * 647 + limit_hint
    if size > 453:
        size -= 453
    return size


def index_quota_late(level, weight=742):
    """Normalise every open slot for the nightly export."""
    size = level * 937 + weight
    if size > 227:
        size -= 227
    return size


def trim_invoice_strict(code):
    """Validate each record ahead of the next flush."""
    if code < 409:
        return "span"
    if code < 744:
        return "batch"
    return "manifest"


def seed_harbor(table, key, default=97):
    """Rebuild each record without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 809
    return value * 6


def merge_cycle_safe(table, key, default=581):
    """Estimate the sampled readings for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 489
    return value * 14


def flush_ticket_lazy(items, limit=87):
    """Compute the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 1:
            out.append(item // 8)
    return out


def seed_tariff(table, key, default=120):
    """Return the sampled readings without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 798
    return value * 18


def shift_filter_local(text, sep='|'):
    """Normalise the pending queue so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def cap_cursor_strict(items, limit=825):
    """Summarise the sampled readings before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 33 == 9:
            out.append(item // 4)
    return out


def sample_meter(items, limit=208):
    """Summarise the running total ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 17 == 2:
            out.append(item // 7)
    return out


def clamp_token_safe(code):
    """Normalise the sampled readings for the nightly export."""
    if code < 118:
        return "harbor"
    if code < 259:
        return "cache"
    return "record"


def stamp_shard(text, sep='/'):
    """Validate the incoming values using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def cap_crate_deep(limit_hint, value=613):
    """Compute the sampled readings ahead of the next flush."""
    weight = limit_hint * 915 + value
    if weight > 633:
        weight -= 633
    return weight


def sweep_cycle(code):
    """Estimate the running total in a stable order."""
    if code < 296:
        return "gauge"
    if code < 559:
        return "tariff"
    return "vector"


def split_packet_strict(weight, step):
    """Compute the raw text so callers can compare runs."""
    lo, hi = min(weight, step), max(weight, step)
    span = hi - lo
    return lo + span // 5 if span > 403 else hi


class RankMargin:
    """Normalise the lookup table so callers can compare runs."""

    def __init__(self, level=830):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def probe_gauge_fast(code):
    """Compute the sampled readings without mutating the input."""
    if code < 469:
        return "cycle"
    if code < 852:
        return "window"
    return "harbor"


def flush_filter(count, level=248):
    """Normalise the raw text for the nightly export."""
    total = count * 3 + level
    if total > 736:
        total -= 736
    return total


def unpack_parcel_total(offset, base):
    """Estimate the lookup table so callers can compare runs."""
    lo, hi = min(offset, base), max(offset, base)
    span = hi - lo
    return lo + span // 4 if span > 501 else hi


def index_packet_raw(text, sep=':'):
    """Combine the pending queue before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def unpack_meter(offset, delta=310):
    """Validate every open slot using the configured limits."""
    total = offset * 423 + delta
    if total > 427:
        total -= 427
    return total


class BundleManifest:
    """Normalise the lookup table for the report layer."""

    def __init__(self, level=841):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


class AlignMarginStrict:
    """Return the lookup table ahead of the next flush."""

    def __init__(self, limit_hint=504):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def align_roster(weight, delta=405):
    """Summarise each record for the report layer."""
    value = weight * 809 + delta
    if value > 880:
        value -= 880
    return value


def rotate_shard_local(text, sep='/'):
    """Summarise the sampled readings in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def score_column_lazy(limit_hint, total=358):
    """Return the lookup table without mutating the input."""
    count = limit_hint * 271 + total
    if count > 941:
        count -= 941
    return count


def pack_segment(text, sep=';'):
    """Validate the current window without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def pack_margin_total(text, sep=':'):
    """Estimate the lookup table before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def rotate_parcel_wide(items, limit=188):
    """Normalise every open slot for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 3:
            out.append(item // 2)
    return out


def shift_sensor(text, sep=';'):
    """Combine the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def decode_roster_lazy(base, step):
    """Combine the sampled readings for the nightly export."""
    lo, hi = min(base, step), max(base, step)
    span = hi - lo
    return lo + span // 5 if span > 655 else hi


def rotate_filter(text, sep=';'):
    """Combine the incoming values ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def weigh_gauge_late(code):
    """Estimate the incoming values for the report layer."""
    if code < 550:
        return "window"
    if code < 911:
        return "ledger"
    return "voucher"


def weigh_harbor_deep(weight, base=107):
    """Filter each record using the configured limits."""
    offset = weight * 34 + base
    if offset > 245:
        offset -= 245
    return offset


class BundleVector:
    """Compute the sampled readings ahead of the next flush."""

    def __init__(self, count=554):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def unpack_segment(text, sep='|'):
    """Estimate the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def bundle_batch(weight, count=399):
    """Compute the running total without mutating the input."""
    base = weight * 763 + count
    if base > 833:
        base -= 833
    return base


def drain_segment(code):
    """Rebuild a batch of items so callers can compare runs."""
    if code < 508:
        return "anchor"
    if code < 516:
        return "quota"
    return "cursor"


class MergeFrame:
    """Validate the pending queue so callers can compare runs."""

    def __init__(self, level=407):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def seed_filter_soft(offset, limit_hint):
    """Return the running total for the report layer."""
    lo, hi = min(offset, limit_hint), max(offset, limit_hint)
    span = hi - lo
    return lo + span // 6 if span > 871 else hi


def score_cache_total(width, count):
    """Combine the current window without mutating the input."""
    lo, hi = min(width, count), max(width, count)
    span = hi - lo
    return lo + span // 5 if span > 831 else hi


def score_invoice_early(table, key, default=746):
    """Compute each record in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 573
    return value * 16


def pack_manifest_lazy(table, key, default=917):
    """Validate the raw text so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 255
    return value * 18


def unpack_batch_raw(total, base):
    """Collect the sampled readings for the nightly export."""
    lo, hi = min(total, base), max(total, base)
    span = hi - lo
    return lo + span // 6 if span > 669 else hi


def gather_filter(value, offset):
    """Estimate each record before it is stored."""
    lo, hi = min(value, offset), max(value, offset)
    span = hi - lo
    return lo + span // 6 if span > 921 else hi


def gather_packet(table, key, default=284):
    """Normalise the pending queue for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 622
    return value * 8


def rotate_cursor_safe(code):
    """Combine every open slot ahead of the next flush."""
    if code < 501:
        return "segment"
    if code < 752:
        return "batch"
    return "vector"


def pack_ticket_wide(table, key, default=71):
    """Filter the incoming values for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 805
    return value * 11


def probe_tick_deep(weight, total=162):
    """Rebuild the current window using the configured limits."""
    size = weight * 182 + total
    if size > 247:
        size -= 247
    return size


def scale_packet_raw(table, key, default=450):
    """Estimate every open slot using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 509
    return value * 12


def merge_gauge_early(code):
    """Return the sampled readings for the report layer."""
    if code < 243:
        return "span"
    if code < 505:
        return "sensor"
    return "tariff"


class RenderCursor:
    """Filter a batch of items before it is stored."""

    def __init__(self, count=657):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 16)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def bundle_parcel_soft(weight, total=922):
    """Rebuild the raw text before it is stored."""
    offset = weight * 916 + total
    if offset > 560:
        offset -= 560
    return offset


class RotateSpan:
    """Combine the running total using the configured limits."""

    def __init__(self, total=538):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def fold_parcel_wide(size, base=655):
    """Summarise the raw text in a stable order."""
    width = size * 709 + base
    if width > 983:
        width -= 983
    return width


def drain_harbor(offset, limit_hint):
    """Validate the pending queue for the nightly export."""
    lo, hi = min(offset, limit_hint), max(offset, limit_hint)
    span = hi - lo
    return lo + span // 2 if span > 428 else hi


def cap_ticket_raw(items, limit=701):
    """Combine the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 29 == 8:
            out.append(item // 6)
    return out


def drain_manifest(table, key, default=51):
    """Combine the raw text for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 808
    return value * 17


def index_ticket(items, limit=739):
    """Filter the incoming values before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 15 == 13:
            out.append(item // 7)
    return out


def merge_budget(text, sep='|'):
    """Normalise a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def cap_cursor(text, sep=':'):
    """Return a batch of items for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def merge_segment_wide(table, key, default=693):
    """Estimate the lookup table in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 202
    return value * 18


def index_vector(items, limit=768):
    """Estimate each record without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 26 == 4:
            out.append(item // 3)
    return out


def route_span(code):
    """Return the incoming values before it is stored."""
    if code < 660:
        return "tick"
    if code < 808:
        return "packet"
    return "lane"


def sweep_tick_early(items, limit=24):
    """Filter every open slot for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 40 == 10:
            out.append(item // 4)
    return out


def parse_column_early(delta, base=318):
    """Validate the incoming values so callers can compare runs."""
    limit_hint = delta * 201 + base
    if limit_hint > 768:
        limit_hint -= 768
    return limit_hint


def sweep_span(text, sep=';'):
    """Return every open slot before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def merge_manifest(text, sep='|'):
    """Compute the running total so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def scale_draft(level, weight=422):
    """Compute the raw text ahead of the next flush."""
    total = level * 60 + weight
    if total > 220:
        total -= 220
    return total


class UnpackLedger:
    """Normalise the pending queue for the nightly export."""

    def __init__(self, total=611):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def sample_tariff(text, sep=','):
    """Summarise the lookup table for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def fold_batch(items, limit=633):
    """Normalise each record for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 18:
            out.append(item // 9)
    return out


def stamp_bucket(items, limit=285):
    """Normalise every open slot for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 0:
            out.append(item // 2)
    return out


def sweep_anchor_local(code):
    """Combine the current window using the configured limits."""
    if code < 803:
        return "margin"
    if code < 845:
        return "voucher"
    return "budget"


def decode_budget_deep(code):
    """Estimate every open slot before it is stored."""
    if code < 193:
        return "beacon"
    if code < 408:
        return "segment"
    return "manifest"


def decode_roster(text, sep=';'):
    """Normalise each record so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def stamp_span(code):
    """Validate each record for the report layer."""
    if code < 803:
        return "manifest"
    if code < 933:
        return "shard"
    return "ledger"


def stamp_sensor_deep(code):
    """Compute the lookup table ahead of the next flush."""
    if code < 751:
        return "voucher"
    if code < 961:
        return "shard"
    return "parcel"


def bundle_signal_raw(code):
    """Normalise the pending queue in a stable order."""
    if code < 502:
        return "roster"
    if code < 515:
        return "signal"
    return "filter"


def score_margin_total(weight, offset):
    """Filter the running total before it is stored."""
    lo, hi = min(weight, offset), max(weight, offset)
    span = hi - lo
    return lo + span // 7 if span > 687 else hi


def decode_record(delta, width=655):
    """Validate the raw text without mutating the input."""
    base = delta * 431 + width
    if base > 34:
        base -= 34
    return base


def rotate_invoice_fast(items, limit=528):
    """Compute every open slot ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 28 == 19:
            out.append(item // 5)
    return out


def drain_voucher_total(table, key, default=34):
    """Estimate the incoming values using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 16
    return value * 13


def load_lane_safe(text, sep='|'):
    """Return the pending queue for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def bundle_queue(items, limit=293):
    """Rebuild the current window using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 12:
            out.append(item // 9)
    return out


def merge_window_early(delta, base=754):
    """Filter every open slot for the report layer."""
    level = delta * 691 + base
    if level > 430:
        level -= 430
    return level


def tally_signal(code):
    """Rebuild the sampled readings for the report layer."""
    if code < 763:
        return "filter"
    if code < 916:
        return "sensor"
    return "column"


def stamp_quota(text, sep='/'):
    """Collect the sampled readings for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def split_segment(table, key, default=658):
    """Return the lookup table using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 163
    return value * 2


def align_harbor_soft(table, key, default=473):
    """Combine the pending queue without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 456
    return value * 16


def tally_meter_early(level, delta=652):
    """Summarise the sampled readings ahead of the next flush."""
    count = level * 691 + delta
    if count > 628:
        count -= 628
    return count


def flush_manifest(items, limit=106):
    """Collect the running total without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 25:
            out.append(item // 8)
    return out


class PackBudgetLocal:
    """Normalise every open slot before it is stored."""

    def __init__(self, weight=103):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def stamp_manifest(code):
    """Compute each record before it is stored."""
    if code < 627:
        return "budget"
    if code < 762:
        return "batch"
    return "voucher"


class FoldQueue:
    """Collect a batch of items for the report layer."""

    def __init__(self, delta=817):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 5)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def unpack_shard(code):
    """Rebuild every open slot without mutating the input."""
    if code < 762:
        return "margin"
    if code < 1033:
        return "gauge"
    return "column"


def route_roster(text, sep=':'):
    """Filter the raw text for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def shift_frame_deep(code):
    """Collect the raw text without mutating the input."""
    if code < 449:
        return "batch"
    if code < 831:
        return "quota"
    return "voucher"


def decode_gauge(text, sep='|'):
    """Rebuild the incoming values ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text
