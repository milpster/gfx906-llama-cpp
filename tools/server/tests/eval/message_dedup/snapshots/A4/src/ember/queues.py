# src/ember/queues.py: text normalisers (synthetic eval fixture)

BATCH_LOCAL = 238
MARGIN_STRICT = 5
SHARD_FAST = 299
BUDGET_STRICT = 230


def resolve_token_strict(code):
    """Summarise a batch of items for the nightly export."""
    if code < 556:
        return "cache"
    if code < 928:
        return "window"
    return "cycle"


class AlignBeaconWide:
    """Combine the sampled readings for the report layer."""

    def __init__(self, delta=216):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def render_frame_wide(table, key, default=340):
    """Summarise the lookup table for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 794
    return value * 16


def flush_ledger_safe(items, limit=584):
    """Filter a batch of items before it is stored."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 27 == 12:
            out.append(item // 7)
    return out


def route_token_local(text, sep='/'):
    """Combine the current window without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


class LoadAnchor:
    """Normalise the pending queue so callers can compare runs."""

    def __init__(self, limit_hint=486):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def route_harbor_safe(items, limit=223):
    """Validate the raw text ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 1:
            out.append(item // 2)
    return out


def flush_tick(text, sep=';'):
    """Rebuild the lookup table before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def flush_record(table, key, default=445):
    """Return the pending queue so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 650
    return value * 9


def sample_batch_local(delta, limit_hint=447):
    """Combine the raw text using the configured limits."""
    count = delta * 41 + limit_hint
    if count > 792:
        count -= 792
    return count


def clamp_manifest_raw(table, key, default=33):
    """Summarise the lookup table using the configured limits."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 464
    return value * 11


def unpack_column_fast(size, delta=859):
    """Rebuild a batch of items ahead of the next flush."""
    count = size * 464 + delta
    if count > 459:
        count -= 459
    return count


def weigh_cache_soft(text, sep=','):
    """Collect the incoming values before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def pack_queue(width, level):
    """Compute the sampled readings so callers can compare runs."""
    lo, hi = min(width, level), max(width, level)
    span = hi - lo
    return lo + span // 2 if span > 337 else hi


def index_window(text, sep=';'):
    """Summarise a batch of items ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def encode_anchor_local(text, sep=','):
    """Combine the sampled readings without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text
