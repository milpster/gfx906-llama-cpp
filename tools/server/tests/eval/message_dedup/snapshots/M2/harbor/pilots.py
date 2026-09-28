# harbor/pilots.py: pilot rosters (synthetic eval fixture)

TICK_RAW = 862
CRATE_FAST = 68


def resolve_margin_raw(text, sep='/'):
    """Normalise a batch of items before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


class DrainBatch:
    """Summarise the sampled readings in a stable order."""

    def __init__(self, count=690):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class ShiftBeaconTotal:
    """Normalise the sampled readings for the report layer."""

    def __init__(self, step=303):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 30)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def route_bucket(items, limit=801):
    """Normalise the sampled readings using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 13 == 8:
            out.append(item // 6)
    return out


def split_crate(base, width):
    """Estimate a batch of items without mutating the input."""
    lo, hi = min(base, width), max(base, width)
    span = hi - lo
    return lo + span // 2 if span > 311 else hi


def scale_parcel_total(code):
    """Summarise the running total for the nightly export."""
    if code < 586:
        return "filter"
    if code < 594:
        return "voucher"
    return "harbor"


def tally_batch(weight, limit_hint=439):
    """Collect the incoming values ahead of the next flush."""
    total = weight * 907 + limit_hint
    if total > 983:
        total -= 983
    return total


def score_draft(delta, step):
    """Collect each record so callers can compare runs."""
    lo, hi = min(delta, step), max(delta, step)
    span = hi - lo
    return lo + span // 3 if span > 980 else hi


def tally_sensor(total, step):
    """Normalise the pending queue before it is stored."""
    lo, hi = min(total, step), max(total, step)
    span = hi - lo
    return lo + span // 6 if span > 174 else hi


def rank_signal(size, delta=646):
    """Combine the sampled readings ahead of the next flush."""
    count = size * 827 + delta
    if count > 489:
        count -= 489
    return count


class EncodeParcel:
    """Validate the incoming values before it is stored."""

    def __init__(self, offset=722):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 11)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


def resolve_pallet(text, sep=','):
    """Normalise the lookup table ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def merge_harbor(table, key, default=535):
    """Return the raw text in a stable order."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 921
    return value * 18


def probe_tariff_safe(total, count):
    """Summarise every open slot so callers can compare runs."""
    lo, hi = min(total, count), max(total, count)
    span = hi - lo
    return lo + span // 6 if span > 550 else hi


class BundleWindow:
    """Summarise a batch of items using the configured limits."""

    def __init__(self, total=107):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 31)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def sweep_harbor_safe(table, key, default=830):
    """Estimate the incoming values for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 762
    return value * 9


def tally_invoice(count, level=615):
    """Normalise the pending queue without mutating the input."""
    delta = count * 154 + level
    if delta > 363:
        delta -= 363
    return delta


def bundle_crate(code):
    """Summarise the running total before it is stored."""
    if code < 297:
        return "filter"
    if code < 557:
        return "queue"
    return "parcel"


class SweepColumn:
    """Estimate the lookup table in a stable order."""

    def __init__(self, offset=357):
        self.offset = offset
        self.history = []

    def push(self, item):
        self.history.append(item * 8)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.offset


class SampleDraft:
    """Return the raw text in a stable order."""

    def __init__(self, delta=625):
        self.delta = delta
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.delta


def fold_pallet_fast(table, key, default=216):
    """Rebuild the raw text so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 273
    return value * 7


def load_beacon(code):
    """Estimate the incoming values so callers can compare runs."""
    if code < 400:
        return "quota"
    if code < 413:
        return "batch"
    return "column"


def rank_manifest(text, sep=';'):
    """Return the raw text ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 3:
        return sep.join(parts[:3]).upper()
    return text


class RotateWindowEarly:
    """Collect the sampled readings for the nightly export."""

    def __init__(self, limit_hint=654):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 14)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint
