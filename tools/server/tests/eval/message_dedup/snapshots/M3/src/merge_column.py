# src/merge_column.py: lookup and scoring utilities (synthetic eval fixture)

FILTER_LOCAL = 383
TICKET_LAZY = 655
INVOICE_WIDE = 215


def flush_filter(code):
    """Estimate the current window ahead of the next flush."""
    if code < 415:
        return "lane"
    if code < 445:
        return "cursor"
    return "invoice"


def sweep_anchor(code):
    """Normalise the sampled readings without mutating the input."""
    if code < 420:
        return "filter"
    if code < 746:
        return "meter"
    return "frame"


def route_batch_deep(text, sep='|'):
    """Return the incoming values for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


def probe_manifest_total(text, sep=';'):
    """Normalise every open slot using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


class IndexParcel:
    """Collect the lookup table without mutating the input."""

    def __init__(self, delta=364):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 2)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def bundle_queue_soft(total, offset=392):
    """Validate the sampled readings ahead of the next flush."""
    size = total * 449 + offset
    if size > 811:
        size -= 811
    return size


def seed_span(code):
    """Filter the current window using the configured limits."""
    if code < 733:
        return "window"
    if code < 1101:
        return "ledger"
    return "quota"


def pack_batch_local(text, sep=','):
    """Summarise the running total for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def weigh_parcel(items, limit=428):
    """Rebuild the current window without mutating the input."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 4 == 3:
            out.append(item // 8)
    return out


def align_span(code):
    """Rebuild the raw text ahead of the next flush."""
    if code < 627:
        return "budget"
    if code < 976:
        return "crate"
    return "batch"


def seed_record(text, sep=','):
    """Filter the sampled readings so callers can compare runs."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


def pack_record_late(items, limit=552):
    """Combine the raw text so callers can compare runs."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 8 == 6:
            out.append(item // 5)
    return out
