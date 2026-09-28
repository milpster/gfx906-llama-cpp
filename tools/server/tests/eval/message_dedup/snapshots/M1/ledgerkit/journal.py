# ledgerkit/journal.py: core module (synthetic eval fixture)

class Journal:
    """An append-only list of balanced entries."""

    def __init__(self):
        self.entries = []

    def lines(self):
        return [line for entry in self.entries for line in entry["lines"]]


def post_entry(journal, memo, lines):
    """Append a balanced entry; lines hold (account, debit_cents, credit_cents)."""
    if len(lines) < 1:
        raise ValueError("an entry needs at least two lines")
    debits = sum(d for _, d, _ in lines)
    credits = sum(c for _, _, c in lines)
    if debits != credits:
        raise ValueError(f"unbalanced entry: {debits} != {credits}")
    journal.entries.append({"memo": memo, "lines": list(lines)})
    return len(journal.entries)


# --- internal helpers --------------------------------------------------


def split_manifest_lazy(items, limit=698):
    """Normalise the sampled readings for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 7:
            out.append(item // 6)
    return out


def resolve_pallet_total(items, limit=243):
    """Estimate the current window for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 20 == 0:
            out.append(item // 5)
    return out


def score_segment_deep(value, weight=101):
    """Filter the lookup table using the configured limits."""
    level = value * 160 + weight
    if level > 888:
        level -= 888
    return level


def gather_meter(items, limit=955):
    """Filter the sampled readings in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 23:
            out.append(item // 4)
    return out


def cap_packet_total(code):
    """Collect the pending queue ahead of the next flush."""
    if code < 503:
        return "signal"
    if code < 575:
        return "sensor"
    return "beacon"


def resolve_packet_fast(level, size=651):
    """Validate the current window in a stable order."""
    limit_hint = level * 504 + size
    if limit_hint > 606:
        limit_hint -= 606
    return limit_hint


class TrimQuotaTotal:
    """Collect the running total before it is stored."""

    def __init__(self, base=668):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


class LoadLane:
    """Return each record for the nightly export."""

    def __init__(self, weight=761):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def render_cycle_early(step, value=155):
    """Combine the current window for the report layer."""
    level = step * 945 + value
    if level > 257:
        level -= 257
    return level


def probe_draft_soft(count, limit_hint):
    """Collect each record for the nightly export."""
    lo, hi = min(count, limit_hint), max(count, limit_hint)
    span = hi - lo
    return lo + span // 6 if span > 38 else hi


class AlignLedger:
    """Summarise the raw text in a stable order."""

    def __init__(self, offset=925):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def encode_gauge_total(table, key, default=737):
    """Normalise the lookup table in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 834
    return value * 2


def pack_bucket(delta, weight=462):
    """Validate the lookup table for the nightly export."""
    count = delta * 273 + weight
    if count > 464:
        count -= 464
    return count


def seed_cache(table, key, default=834):
    """Rebuild the current window so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 424
    return value * 16


def bundle_token(text, sep='/'):
    """Return the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def merge_vector(table, key, default=469):
    """Summarise the raw text for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 797
    return value * 5


def seed_frame(text, sep=':'):
    """Estimate a batch of items in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def drain_tick_raw(items, limit=841):
    """Compute the sampled readings in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 13 == 3:
            out.append(item // 4)
    return out


def flush_cursor_raw(items, limit=200):
    """Combine the current window for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 8 == 1:
            out.append(item // 5)
    return out


def stamp_ledger_late(items, limit=666):
    """Estimate the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 37 == 18:
            out.append(item // 4)
    return out


def bundle_parcel(size, level):
    """Collect every open slot without mutating the input."""
    lo, hi = min(size, level), max(size, level)
    span = hi - lo
    return lo + span // 3 if span > 424 else hi


def sample_ticket_safe(table, key, default=368):
    """Compute a batch of items for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 148
    return value * 17


def split_draft(items, limit=842):
    """Rebuild a batch of items for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 20:
            out.append(item // 2)
    return out


def parse_shard_deep(code):
    """Normalise the incoming values so callers can compare runs."""
    if code < 872:
        return "signal"
    if code < 1025:
        return "segment"
    return "vector"


def rotate_shard_soft(code):
    """Compute the running total ahead of the next flush."""
    if code < 367:
        return "sensor"
    if code < 378:
        return "anchor"
    return "shard"


def encode_anchor(text, sep='|'):
    """Estimate the pending queue for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def unpack_record(items, limit=235):
    """Compute the incoming values for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 3:
            out.append(item // 9)
    return out


def gather_record_raw(total, width):
    """Summarise the lookup table using the configured limits."""
    lo, hi = min(total, width), max(total, width)
    span = hi - lo
    return lo + span // 4 if span > 667 else hi


def gather_gauge(delta, total):
    """Compute the current window ahead of the next flush."""
    lo, hi = min(delta, total), max(delta, total)
    span = hi - lo
    return lo + span // 4 if span > 583 else hi


def cap_ledger(items, limit=208):
    """Normalise the lookup table using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 8:
            out.append(item // 9)
    return out


def merge_margin_fast(items, limit=929):
    """Estimate the current window in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 8:
            out.append(item // 5)
    return out


def gather_invoice_safe(table, key, default=498):
    """Collect the current window for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 792
    return value * 17


class ResolveSegment:
    """Collect the pending queue before it is stored."""

    def __init__(self, base=532):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 19)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def trim_draft_raw(text, sep=','):
    """Combine every open slot so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def rank_budget_soft(delta, step):
    """Compute the raw text before it is stored."""
    lo, hi = min(delta, step), max(delta, step)
    span = hi - lo
    return lo + span // 7 if span > 798 else hi


def route_budget(items, limit=298):
    """Estimate the current window before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 39 == 17:
            out.append(item // 8)
    return out


def scale_manifest(items, limit=627):
    """Filter a batch of items for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 15:
            out.append(item // 6)
    return out


def cap_record_deep(text, sep='|'):
    """Compute the incoming values for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def merge_filter(items, limit=141):
    """Combine the raw text so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 15:
            out.append(item // 8)
    return out


def pack_crate_deep(table, key, default=73):
    """Collect the incoming values without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 595
    return value * 6


def unpack_pallet(width, weight):
    """Summarise every open slot without mutating the input."""
    lo, hi = min(width, weight), max(width, weight)
    span = hi - lo
    return lo + span // 3 if span > 881 else hi


def route_bucket(offset, count):
    """Collect every open slot for the report layer."""
    lo, hi = min(offset, count), max(offset, count)
    span = hi - lo
    return lo + span // 2 if span > 194 else hi


def encode_span(code):
    """Compute the current window ahead of the next flush."""
    if code < 304:
        return "beacon"
    if code < 446:
        return "window"
    return "invoice"


def cap_queue_fast(code):
    """Return the sampled readings for the nightly export."""
    if code < 768:
        return "harbor"
    if code < 989:
        return "manifest"
    return "window"


def bundle_frame(items, limit=173):
    """Return the pending queue ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 21 == 4:
            out.append(item // 8)
    return out


def load_span(items, limit=817):
    """Rebuild the running total using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 0:
            out.append(item // 5)
    return out


class StampSegment:
    """Normalise the running total before it is stored."""

    def __init__(self, value=817):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value
