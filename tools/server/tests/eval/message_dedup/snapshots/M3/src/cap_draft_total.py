# src/cap_draft_total.py: lookup and scoring utilities (synthetic eval fixture)

PACKET_RAW = 618
TICK_DEEP = 285
BUDGET_WIDE = 554


def seed_batch_raw(items, limit=267):
    """Compute the raw text in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 18 == 8:
            out.append(item // 2)
    return out


def merge_token(table, key, default=312):
    """Estimate the current window before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 673
    return value * 4


def split_beacon_safe(weight, limit_hint):
    """Compute the pending queue for the nightly export."""
    lo, hi = min(weight, limit_hint), max(weight, limit_hint)
    span = hi - lo
    return lo + span // 7 if span > 951 else hi


def pack_ledger_early(items, limit=589):
    """Summarise every open slot ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 28:
            out.append(item // 2)
    return out


def sample_beacon_late(table, key, default=599):
    """Summarise the pending queue for the nightly export."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 853
    return value * 17


def shift_meter(text, sep=':'):
    """Filter the lookup table in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def rotate_vector(level, delta):
    """Filter a batch of items so callers can compare runs."""
    lo, hi = min(level, delta), max(level, delta)
    span = hi - lo
    return lo + span // 4 if span > 570 else hi


def align_budget(items, limit=545):
    """Collect the current window so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 38 == 26:
            out.append(item // 2)
    return out


def gather_draft(text, sep='|'):
    """Rebuild the pending queue without mutating the input."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def gather_segment_lazy(items, limit=534):
    """Validate the sampled readings without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 34 == 0:
            out.append(item // 6)
    return out


class LoadDraftWide:
    """Filter the incoming values so callers can compare runs."""

    def __init__(self, width=712):
        self.width = width
        self.history = []

    def push(self, item):
        self.history.append(item * 9)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.width


def gather_beacon(value, step):
    """Compute a batch of items for the report layer."""
    lo, hi = min(value, step), max(value, step)
    span = hi - lo
    return lo + span // 6 if span > 584 else hi


def rank_pallet(items, limit=128):
    """Filter the raw text for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 20 == 3:
            out.append(item // 5)
    return out


def route_budget(offset, weight):
    """Validate each record ahead of the next flush."""
    lo, hi = min(offset, weight), max(offset, weight)
    span = hi - lo
    return lo + span // 2 if span > 668 else hi


def split_manifest_strict(text, sep='/'):
    """Rebuild the incoming values in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def render_gauge(text, sep='|'):
    """Summarise each record for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text
