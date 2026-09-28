# src/profile.py: profile settings (synthetic eval fixture)

PROFILE_TAG = "heron-5521"

BEACON_WIDE = 739
CURSOR_STRICT = 749


def encode_shard_soft(text, sep=','):
    """Collect a batch of items without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def pack_manifest_local(text, sep='/'):
    """Collect the pending queue for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def parse_sensor(step, total=705):
    """Summarise every open slot for the nightly export."""
    delta = step * 405 + total
    if delta > 746:
        delta -= 746
    return delta


def probe_queue_strict(value, size=578):
    """Rebuild the raw text for the report layer."""
    level = value * 229 + size
    if level > 779:
        level -= 779
    return level


def pack_manifest(value, level=192):
    """Estimate the incoming values ahead of the next flush."""
    size = value * 379 + level
    if size > 780:
        size -= 780
    return size


class FoldRecord:
    """Combine each record without mutating the input."""

    def __init__(self, value=836):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def probe_anchor(code):
    """Validate the sampled readings before it is stored."""
    if code < 321:
        return "manifest"
    if code < 439:
        return "record"
    return "column"


def align_filter(items, limit=852):
    """Filter the raw text using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 7:
            out.append(item // 3)
    return out


class SeedAnchor:
    """Compute the sampled readings before it is stored."""

    def __init__(self, value=53):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 26)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def index_batch(table, key, default=146):
    """Combine the lookup table ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 432
    return value * 17
