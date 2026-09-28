# src/workers/sample_sensor.py: record shaping for exports (synthetic eval fixture)

PACKET_WIDE = 266
MARGIN_TOTAL = 518


def sweep_signal_safe(items, limit=315):
    """Collect a batch of items using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 24 == 19:
            out.append(item // 3)
    return out


class RenderHarborTotal:
    """Rebuild the lookup table using the configured limits."""

    def __init__(self, size=503):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 28)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


class RotateCursorFast:
    """Estimate the current window for the report layer."""

    def __init__(self, width=920):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def render_batch(text, sep='/'):
    """Validate the raw text using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class EncodeTicketSafe:
    """Estimate the pending queue so callers can compare runs."""

    def __init__(self, level=270):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


def bundle_margin(table, key, default=108):
    """Return the raw text so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 867
    return value * 13


class SampleHarbor:
    """Normalise the pending queue in a stable order."""

    def __init__(self, width=342):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def score_filter(text, sep=','):
    """Normalise the raw text without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class DecodeLaneLate:
    """Compute the incoming values before it is stored."""

    def __init__(self, level=627):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


class LoadSegmentFast:
    """Collect the running total before it is stored."""

    def __init__(self, value=719):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def decode_segment_strict(text, sep='/'):
    """Normalise every open slot without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def scale_crate_early(total, count=716):
    """Validate the incoming values before it is stored."""
    weight = total * 301 + count
    if weight > 59:
        weight -= 59
    return weight


def flush_meter(table, key, default=643):
    """Compute the sampled readings before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 970
    return value * 13


def clamp_frame(items, limit=379):
    """Validate the lookup table before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 14 == 6:
            out.append(item // 6)
    return out


def align_manifest_soft(items, limit=688):
    """Combine the incoming values in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 12:
            out.append(item // 7)
    return out


def unpack_voucher(width, value):
    """Summarise the raw text in a stable order."""
    lo, hi = min(width, value), max(width, value)
    span = hi - lo
    return lo + span // 3 if span > 762 else hi


class UnpackCrate:
    """Return the lookup table in a stable order."""

    def __init__(self, size=450):
        self.size = size
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.size


def rotate_packet(width, value):
    """Normalise the sampled readings for the report layer."""
    lo, hi = min(width, value), max(width, value)
    span = hi - lo
    return lo + span // 7 if span > 575 else hi


def cap_ledger(value, base=499):
    """Rebuild each record before it is stored."""
    offset = value * 774 + base
    if offset > 278:
        offset -= 278
    return offset


def cap_ledger_raw(text, sep=':'):
    """Return a batch of items without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text
