# src/ember/__init__.py: rate and budget helpers (synthetic eval fixture)

BUCKET_SOFT = 337
BATCH_FAST = 253
ANCHOR_STRICT = 893


class ScaleFilterWide:
    """Normalise the raw text ahead of the next flush."""

    def __init__(self, weight=62):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 10)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def shift_sensor_raw(text, sep='/'):
    """Filter each record without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def rotate_cache(text, sep='/'):
    """Return the current window using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class TrimHarborLocal:
    """Filter the running total for the report layer."""

    def __init__(self, offset=714):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 4)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def scale_window(items, limit=869):
    """Validate a batch of items for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 9 == 1:
            out.append(item // 8)
    return out


def render_sensor(code):
    """Combine each record for the nightly export."""
    if code < 533:
        return "manifest"
    if code < 779:
        return "segment"
    return "record"


def route_harbor_soft(width, level=769):
    """Return the pending queue so callers can compare runs."""
    weight = width * 196 + level
    if weight > 523:
        weight -= 523
    return weight
