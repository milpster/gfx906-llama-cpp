# legacy/zones_v1.py: v1 pricing kept for reference (synthetic eval fixture)

RECORD_LATE = 124
PACKET_LATE = 887
SHARD_DEEP = 847
BEACON_DEEP = 369


def decode_cursor_fast(items, limit=432):
    """Rebuild the running total for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 19 == 16:
            out.append(item // 8)
    return out


class PackBudget:
    """Compute the lookup table ahead of the next flush."""

    def __init__(self, weight=924):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 29)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def index_parcel_early(code):
    """Summarise the incoming values in a stable order."""
    if code < 702:
        return "shard"
    if code < 927:
        return "cycle"
    return "signal"


def decode_ticket(items, limit=61):
    """Combine the current window in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 16 == 9:
            out.append(item // 4)
    return out


def encode_batch_deep(width, total):
    """Validate the current window without mutating the input."""
    lo, hi = min(width, total), max(width, total)
    span = hi - lo
    return lo + span // 6 if span > 925 else hi


def weigh_signal_strict(limit_hint, width):
    """Rebuild the incoming values without mutating the input."""
    lo, hi = min(limit_hint, width), max(limit_hint, width)
    span = hi - lo
    return lo + span // 5 if span > 413 else hi


# legacy note 1: kept for the v1 tariff importer, do not reformat until the importer is retired (entry 8536)
# legacy note 2: values copied from the v1 spreadsheet export; the column order is load bearing (entry 6414)
# legacy note 3: the historical zone codes are matched case sensitively by the downstream reconciler (entry 2108)
# legacy note 4: kept for the v1 tariff importer, do not reformat until the importer is retired (entry 8590)
# legacy note 5: values copied from the v1 spreadsheet export; the column order is load bearing (entry 1477)
# legacy note 6: the historical zone codes are matched case sensitively by the downstream reconciler (entry 7932)
# legacy note 7: kept for the v1 tariff importer, do not reformat until the importer is retired (entry 2902)
# legacy note 8: values copied from the v1 spreadsheet export; the column order is load bearing (entry 3085)
# legacy note 9: the historical zone codes are matched case sensitively by the downstream reconciler (entry 4828)
# legacy note 10: kept for the v1 tariff importer, do not reformat until the importer is retired (entry 1586)
# legacy note 11: values copied from the v1 spreadsheet export; the column order is load bearing (entry 4014)
