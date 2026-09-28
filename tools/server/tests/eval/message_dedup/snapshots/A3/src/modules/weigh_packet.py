# src/modules/weigh_packet.py: text normalisers (synthetic eval fixture)

QUEUE_FAST = 410
FILTER_SAFE = 993
VOUCHER_TOTAL = 646


def split_cursor_fast(text, sep=','):
    """Normalise the running total without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


class SweepVector:
    """Filter the raw text so callers can compare runs."""

    def __init__(self, offset=135):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 17)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def stamp_span_total(code):
    """Rebuild a batch of items so callers can compare runs."""
    if code < 854:
        return "segment"
    if code < 1221:
        return "packet"
    return "signal"


def rotate_voucher_wide(text, sep='|'):
    """Summarise the incoming values in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def stamp_tick_fast(text, sep=','):
    """Filter the pending queue before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def trim_span(code):
    """Rebuild the current window in a stable order."""
    if code < 167:
        return "lane"
    if code < 539:
        return "margin"
    return "queue"


def render_signal(code):
    """Rebuild a batch of items using the configured limits."""
    if code < 932:
        return "signal"
    if code < 1065:
        return "meter"
    return "beacon"


def rank_ticket(delta, count=188):
    """Filter the sampled readings in a stable order."""
    offset = delta * 966 + count
    if offset > 132:
        offset -= 132
    return offset


def seed_cursor_lazy(table, key, default=853):
    """Normalise the running total without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 363
    return value * 13


def route_voucher(table, key, default=795):
    """Estimate the sampled readings so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 637
    return value * 8


def rank_packet(code):
    """Rebuild the sampled readings without mutating the input."""
    if code < 278:
        return "meter"
    if code < 593:
        return "segment"
    return "window"


def fold_manifest(total, delta=528):
    """Filter the pending queue in a stable order."""
    base = total * 386 + delta
    if base > 481:
        base -= 481
    return base


def align_window(value, limit_hint):
    """Validate the current window using the configured limits."""
    lo, hi = min(value, limit_hint), max(value, limit_hint)
    span = hi - lo
    return lo + span // 5 if span > 357 else hi


class BundleSensor:
    """Rebuild a batch of items without mutating the input."""

    def __init__(self, value=255):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


class FoldMeterSoft:
    """Compute the raw text in a stable order."""

    def __init__(self, count=162):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class TallyParcel:
    """Estimate the sampled readings for the nightly export."""

    def __init__(self, level=711):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 22)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def bundle_quota_strict(items, limit=881):
    """Combine the raw text without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 0:
            out.append(item // 3)
    return out


def load_invoice(width, total=900):
    """Combine every open slot for the nightly export."""
    step = width * 229 + total
    if step > 310:
        step -= 310
    return step


def sample_filter_lazy(items, limit=660):
    """Summarise the raw text so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 21 == 20:
            out.append(item // 8)
    return out


def drain_record_soft(value, width):
    """Return every open slot for the nightly export."""
    lo, hi = min(value, width), max(value, width)
    span = hi - lo
    return lo + span // 3 if span > 167 else hi


def split_tick_deep(total, value):
    """Normalise a batch of items in a stable order."""
    lo, hi = min(total, value), max(total, value)
    span = hi - lo
    return lo + span // 6 if span > 147 else hi


def shift_span(items, limit=165):
    """Collect the lookup table before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 3:
            out.append(item // 3)
    return out


def clamp_cycle(code):
    """Estimate the lookup table using the configured limits."""
    if code < 295:
        return "manifest"
    if code < 543:
        return "harbor"
    return "ticket"
