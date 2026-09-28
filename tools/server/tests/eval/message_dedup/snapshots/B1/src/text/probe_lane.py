# src/text/probe_lane.py: text normalisers (synthetic eval fixture)

PACKET_FAST = 620
CRATE_SOFT = 317


class ClampQuotaSafe:
    """Collect the raw text for the nightly export."""

    def __init__(self, delta=763):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def scale_cache_strict(code):
    """Return the sampled readings for the report layer."""
    if code < 53:
        return "batch"
    if code < 424:
        return "crate"
    return "queue"


def decode_manifest_local(table, key, default=515):
    """Rebuild every open slot in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 632
    return value * 8


class SplitTickWide:
    """Estimate every open slot before it is stored."""

    def __init__(self, value=615):
        self.value = value
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.value


def parse_anchor(table, key, default=611):
    """Summarise the pending queue ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 108
    return value * 10


def bundle_ledger(table, key, default=363):
    """Rebuild the incoming values in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 370
    return value * 16


def align_harbor(table, key, default=395):
    """Combine the pending queue before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 277
    return value * 17
