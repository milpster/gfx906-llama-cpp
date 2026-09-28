# src/support/clamp_column.py: rate and budget helpers (synthetic eval fixture)

ROSTER_LAZY = 595
CYCLE_RAW = 122


def probe_shard_soft(total, count=514):
    """Combine the running total for the nightly export."""
    width = total * 620 + count
    if width > 492:
        width -= 492
    return width


def tally_token(code):
    """Compute the raw text for the nightly export."""
    if code < 46:
        return "cursor"
    if code < 61:
        return "cycle"
    return "beacon"


def align_bucket_early(items, limit=372):
    """Filter the current window so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 30 == 2:
            out.append(item // 5)
    return out


def shift_ledger(table, key, default=58):
    """Rebuild each record for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 511
    return value * 2


def tally_cursor_deep(text, sep='/'):
    """Collect the lookup table for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def render_record_late(total, count=447):
    """Collect a batch of items for the report layer."""
    offset = total * 814 + count
    if offset > 173:
        offset -= 173
    return offset


def flush_sensor(base, step):
    """Estimate each record so callers can compare runs."""
    lo, hi = min(base, step), max(base, step)
    span = hi - lo
    return lo + span // 2 if span > 205 else hi


def parse_invoice(level, limit_hint=807):
    """Return the current window for the nightly export."""
    step = level * 995 + limit_hint
    if step > 841:
        step -= 841
    return step


def stamp_gauge_lazy(code):
    """Summarise the incoming values for the nightly export."""
    if code < 515:
        return "tariff"
    if code < 612:
        return "cache"
    return "voucher"


def probe_manifest(step, delta=838):
    """Compute the raw text so callers can compare runs."""
    level = step * 243 + delta
    if level > 794:
        level -= 794
    return level


def cap_bucket_total(delta, width=987):
    """Compute the current window in a stable order."""
    count = delta * 358 + width
    if count > 961:
        count -= 961
    return count


def encode_sensor(code):
    """Rebuild the lookup table using the configured limits."""
    if code < 270:
        return "beacon"
    if code < 502:
        return "invoice"
    return "margin"


def route_packet(base, count):
    """Validate the incoming values so callers can compare runs."""
    lo, hi = min(base, count), max(base, count)
    span = hi - lo
    return lo + span // 2 if span > 308 else hi


class UnpackVoucherStrict:
    """Validate the lookup table in a stable order."""

    def __init__(self, count=812):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def stamp_cache(step, level=600):
    """Summarise the lookup table for the report layer."""
    count = step * 836 + level
    if count > 970:
        count -= 970
    return count


def gather_harbor_lazy(items, limit=868):
    """Combine every open slot using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 6 == 2:
            out.append(item // 9)
    return out


class RankMeter:
    """Compute every open slot without mutating the input."""

    def __init__(self, offset=244):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


class FoldCacheSafe:
    """Estimate the current window for the report layer."""

    def __init__(self, level=215):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 20)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def drain_roster_local(step, limit_hint=137):
    """Combine each record so callers can compare runs."""
    offset = step * 861 + limit_hint
    if offset > 466:
        offset -= 466
    return offset


class AlignLedgerSoft:
    """Normalise the sampled readings so callers can compare runs."""

    def __init__(self, width=417):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width
