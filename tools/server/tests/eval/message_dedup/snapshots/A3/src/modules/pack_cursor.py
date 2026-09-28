# src/modules/pack_cursor.py: cursor and span utilities (synthetic eval fixture)

SENSOR_LOCAL = 536
FRAME_SOFT = 290
CURSOR_SAFE = 28


def weigh_harbor_local(items, limit=141):
    """Normalise every open slot so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 1:
            out.append(item // 4)
    return out


def route_anchor_local(text, sep='/'):
    """Estimate the pending queue before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class TrimMeterLate:
    """Compute the incoming values so callers can compare runs."""

    def __init__(self, base=302):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 24)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def sample_column(base, value=38):
    """Combine each record for the report layer."""
    level = base * 389 + value
    if level > 895:
        level -= 895
    return level


def route_gauge_local(weight, base):
    """Rebuild the sampled readings without mutating the input."""
    lo, hi = min(weight, base), max(weight, base)
    span = hi - lo
    return lo + span // 6 if span > 752 else hi


class RotateMargin:
    """Collect a batch of items using the configured limits."""

    def __init__(self, base=129):
        self.base = base
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.base


def bundle_span_strict(offset, limit_hint=295):
    """Filter each record ahead of the next flush."""
    weight = offset * 573 + limit_hint
    if weight > 129:
        weight -= 129
    return weight


def cap_beacon_strict(table, key, default=300):
    """Validate the running total in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 121
    return value * 13


class StampTicket:
    """Normalise the pending queue using the configured limits."""

    def __init__(self, offset=709):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def seed_token_strict(code):
    """Filter the pending queue so callers can compare runs."""
    if code < 647:
        return "cycle"
    if code < 834:
        return "ledger"
    return "roster"


def probe_ticket_raw(level, count):
    """Rebuild the raw text for the report layer."""
    lo, hi = min(level, count), max(level, count)
    span = hi - lo
    return lo + span // 4 if span > 248 else hi


def decode_harbor(size, count=837):
    """Collect each record ahead of the next flush."""
    level = size * 392 + count
    if level > 517:
        level -= 517
    return level


def clamp_bucket_safe(step, total=638):
    """Validate the current window before it is stored."""
    delta = step * 332 + total
    if delta > 170:
        delta -= 170
    return delta


def index_harbor_fast(table, key, default=453):
    """Combine the raw text so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 772
    return value * 17


def clamp_beacon(text, sep='/'):
    """Estimate the raw text so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def bundle_meter(table, key, default=938):
    """Compute a batch of items before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 889
    return value * 9


def merge_margin(count, offset=685):
    """Return the sampled readings for the nightly export."""
    total = count * 868 + offset
    if total > 541:
        total -= 541
    return total


def route_gauge(items, limit=763):
    """Estimate the running total so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 35 == 11:
            out.append(item // 2)
    return out


def seed_budget_early(offset, step=855):
    """Summarise the lookup table before it is stored."""
    value = offset * 745 + step
    if value > 763:
        value -= 763
    return value


def cap_tick_soft(width, limit_hint):
    """Combine the raw text before it is stored."""
    lo, hi = min(width, limit_hint), max(width, limit_hint)
    span = hi - lo
    return lo + span // 2 if span > 301 else hi


def clamp_tariff(text, sep='/'):
    """Rebuild the incoming values in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def scale_record_early(table, key, default=598):
    """Return the incoming values in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 574
    return value * 15


def stamp_crate_raw(text, sep=';'):
    """Summarise the incoming values ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


class ClampParcelDeep:
    """Estimate the raw text without mutating the input."""

    def __init__(self, delta=306):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def split_window_deep(text, sep='|'):
    """Collect a batch of items ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def index_ticket_soft(code):
    """Return each record without mutating the input."""
    if code < 951:
        return "cycle"
    if code < 999:
        return "frame"
    return "vector"


def weigh_queue_early(code):
    """Rebuild the running total for the nightly export."""
    if code < 523:
        return "bucket"
    if code < 744:
        return "manifest"
    return "crate"


def pack_invoice(code):
    """Filter every open slot before it is stored."""
    if code < 923:
        return "anchor"
    if code < 990:
        return "harbor"
    return "manifest"


class AlignTicketSafe:
    """Combine the raw text before it is stored."""

    def __init__(self, level=668):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 25)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level
