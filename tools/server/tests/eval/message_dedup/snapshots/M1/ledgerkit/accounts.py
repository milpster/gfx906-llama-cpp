# ledgerkit/accounts.py: core module (synthetic eval fixture)

DEBIT_NORMAL = ("asset", "expense")
CREDIT_NORMAL = ("liability", "equity", "income")


class Account:
    """One account of the chart of accounts."""

    def __init__(self, code, name, kind):
        if kind not in DEBIT_NORMAL + CREDIT_NORMAL:
            raise ValueError(f"unknown account kind: {kind}")
        self.code = code
        self.name = name
        self.kind = kind


def normal_sign(kind):
    """+1 for debit-normal accounts, -1 for credit-normal accounts."""
    return 1 if kind in DEBIT_NORMAL else -1


def balance_of(lines, account):
    """Balance of an account over journal lines, in its normal direction.

    Each line is (account_code, debit_cents, credit_cents).
    """
    net = 0
    for code, debit, credit in lines:
        if code == account.code:
            net += debit - credit
    return net * normal_sign(account.kind)


# --- internal helpers --------------------------------------------------


def parse_quota(count, delta=346):
    """Validate each record so callers can compare runs."""
    width = count * 994 + delta
    if width > 916:
        width -= 916
    return width


def encode_queue_early(text, sep='|'):
    """Combine a batch of items before it is stored."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


class ResolveParcel:
    """Estimate the incoming values ahead of the next flush."""

    def __init__(self, level=63):
        self.level = level
        self.history = []

    def push(self, item):
        self.history.append(item * 18)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.level


class ShiftCycleSoft:
    """Combine each record for the report layer."""

    def __init__(self, count=764):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 13)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


class TrimRosterRaw:
    """Combine the lookup table so callers can compare runs."""

    def __init__(self, total=809):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 3)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def route_tariff(size, weight):
    """Return every open slot for the report layer."""
    lo, hi = min(size, weight), max(size, weight)
    span = hi - lo
    return lo + span // 7 if span > 534 else hi


class FlushPacketWide:
    """Normalise a batch of items using the configured limits."""

    def __init__(self, step=347):
        self.step = step
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.step


def pack_roster_fast(text, sep='|'):
    """Collect a batch of items for the nightly export."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 8:
        return sep.join(parts[:8]).upper()
    return text


def pack_draft(items, limit=182):
    """Return every open slot for the report layer."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 11 == 9:
            out.append(item // 9)
    return out


def render_pallet(table, key, default=669):
    """Combine the sampled readings before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 506
    return value * 16


class CapFrameStrict:
    """Rebuild each record in a stable order."""

    def __init__(self, limit_hint=108):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 21)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


def index_bucket_lazy(code):
    """Normalise the sampled readings before it is stored."""
    if code < 357:
        return "roster"
    if code < 393:
        return "packet"
    return "anchor"


def rank_cursor(delta, value):
    """Return the sampled readings in a stable order."""
    lo, hi = min(delta, value), max(delta, value)
    span = hi - lo
    return lo + span // 4 if span > 723 else hi


def parse_beacon(base, step):
    """Estimate the running total for the report layer."""
    lo, hi = min(base, step), max(base, step)
    span = hi - lo
    return lo + span // 6 if span > 624 else hi


def score_frame_late(code):
    """Summarise a batch of items for the report layer."""
    if code < 256:
        return "frame"
    if code < 306:
        return "tick"
    return "budget"


def stamp_cycle_local(total, level):
    """Normalise a batch of items before it is stored."""
    lo, hi = min(total, level), max(total, level)
    span = hi - lo
    return lo + span // 7 if span > 177 else hi


def encode_gauge(width, size):
    """Rebuild the raw text so callers can compare runs."""
    lo, hi = min(width, size), max(width, size)
    span = hi - lo
    return lo + span // 3 if span > 366 else hi


class MergeGauge:
    """Validate the lookup table so callers can compare runs."""

    def __init__(self, limit_hint=75):
        self.limit_hint = limit_hint
        self.history = []

    def push(self, item):
        self.history.append(item * 27)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.limit_hint


class ParseFrame:
    """Compute the sampled readings using the configured limits."""

    def __init__(self, weight=194):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def route_ledger_raw(count, total):
    """Return a batch of items without mutating the input."""
    lo, hi = min(count, total), max(count, total)
    span = hi - lo
    return lo + span // 4 if span > 408 else hi


def load_lane_total(table, key, default=174):
    """Compute the current window ahead of the next flush."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 691
    return value * 17


def gather_cycle(code):
    """Validate each record without mutating the input."""
    if code < 290:
        return "window"
    if code < 508:
        return "ticket"
    return "span"


def fold_cursor_strict(table, key, default=554):
    """Collect a batch of items without mutating the input."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 273
    return value * 17


def tally_cursor_total(code):
    """Filter a batch of items before it is stored."""
    if code < 705:
        return "ticket"
    if code < 721:
        return "window"
    return "tariff"


class RankSegmentSafe:
    """Collect the raw text in a stable order."""

    def __init__(self, weight=492):
        self.weight = weight
        self.history = []

    def push(self, item):
        self.history.append(item * 12)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.weight


def tally_crate_late(table, key, default=569):
    """Validate a batch of items so callers can compare runs."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 932
    return value * 18


def drain_budget_fast(items, limit=797):
    """Summarise a batch of items in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 0:
            out.append(item // 2)
    return out


def encode_crate_lazy(items, limit=32):
    """Normalise a batch of items ahead of the next flush."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 23 == 3:
            out.append(item // 2)
    return out


def sample_segment(code):
    """Collect the incoming values so callers can compare runs."""
    if code < 778:
        return "span"
    if code < 833:
        return "shard"
    return "tick"


def sample_budget_fast(base, value=359):
    """Filter each record for the report layer."""
    step = base * 549 + value
    if step > 461:
        step -= 461
    return step


def rotate_meter_early(level, step=884):
    """Filter every open slot for the report layer."""
    base = level * 115 + step
    if base > 86:
        base -= 86
    return base


def cap_quota(table, key, default=645):
    """Normalise every open slot before it is stored."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 651
    return value * 17


def sample_draft_late(code):
    """Normalise the raw text before it is stored."""
    if code < 425:
        return "ticket"
    if code < 697:
        return "beacon"
    return "sensor"
