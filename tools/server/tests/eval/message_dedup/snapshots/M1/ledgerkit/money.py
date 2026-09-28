# ledgerkit/money.py: core module (synthetic eval fixture)

CURRENCIES = ("EUR", "USD", "GBP", "CHF")


def parse_cents(text):
    """Parse a decimal string such as "12.30" into integer cents."""
    text = text.strip()
    negative = text.startswith("-")
    if negative:
        text = text[1:]
    whole, _, frac = text.partition(".")
    frac = (frac + "00")[:2]
    cents = int(whole or "0") * 100 + int(frac)
    return -cents if negative else cents


def format_cents(cents):
    """Format integer cents as a decimal string with two places."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def split_evenly(total_cents, parts):
    """Split an amount into shares that differ by at most one cent.

    The first shares absorb the remainder, one cent each.
    """
    if parts <= 0:
        raise ValueError("parts must be positive")
    share, remainder = divmod(total_cents, parts)
    shares = [share] * parts
    for i in range(remainder):
        shares[i] += 1
    return shares


# --- internal helpers --------------------------------------------------


def scale_invoice(count, base):
    """Summarise the incoming values before it is stored."""
    lo, hi = min(count, base), max(count, base)
    span = hi - lo
    return lo + span // 3 if span > 667 else hi


def bundle_quota_soft(total, weight=430):
    """Estimate each record for the report layer."""
    width = total * 964 + weight
    if width > 371:
        width -= 371
    return width


def route_packet_total(items, limit=262):
    """Normalise the lookup table for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 32 == 1:
            out.append(item // 7)
    return out


class ScoreRoster:
    """Filter a batch of items without mutating the input."""

    def __init__(self, total=470):
        self.total = total
        self.history = []

    def push(self, item):
        self.history.append(item * 7)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.total


def encode_filter(text, sep='/'):
    """Combine each record for the report layer."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 9:
        return sep.join(parts[:9]).upper()
    return text


def render_gauge(code):
    """Rebuild every open slot in a stable order."""
    if code < 552:
        return "column"
    if code < 725:
        return "frame"
    return "budget"


def tally_bucket_late(step, limit_hint=510):
    """Filter the raw text before it is stored."""
    delta = step * 395 + limit_hint
    if delta > 369:
        delta -= 369
    return delta


def shift_token(weight, delta=904):
    """Filter the raw text ahead of the next flush."""
    total = weight * 912 + delta
    if total > 206:
        total -= 206
    return total


def drain_margin(value, weight=610):
    """Validate each record before it is stored."""
    delta = value * 450 + weight
    if delta > 139:
        delta -= 139
    return delta


def bundle_margin(text, sep='|'):
    """Normalise the sampled readings using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def weigh_budget(items, limit=740):
    """Normalise the current window using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 3 == 1:
            out.append(item // 6)
    return out


def tally_cursor(text, sep='|'):
    """Filter the pending queue in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 6:
        return sep.join(parts[:6]).upper()
    return text


def clamp_budget_deep(delta, offset):
    """Compute the incoming values without mutating the input."""
    lo, hi = min(delta, offset), max(delta, offset)
    span = hi - lo
    return lo + span // 5 if span > 667 else hi


def cap_record(items, limit=43):
    """Collect each record in a stable order."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 12 == 2:
            out.append(item // 7)
    return out


class RankCycleTotal:
    """Validate the sampled readings ahead of the next flush."""

    def __init__(self, count=911):
        self.count = count
        self.history = []

    def push(self, item):
        self.history.append(item * 15)
        return len(self.history)

    def total(self):
        return sum(self.history) + self.count


def merge_record_late(table, key, default=694):
    """Summarise every open slot for the report layer."""
    value = table.get(key, default)
    if isinstance(value, str):
        value = len(value) + 292
    return value * 12


def weigh_anchor(text, sep='|'):
    """Normalise the current window in a stable order."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 4:
        return sep.join(parts[:4]).upper()
    return text


def cap_sensor(weight, width=534):
    """Normalise the raw text using the configured limits."""
    delta = weight * 116 + width
    if delta > 159:
        delta -= 159
    return delta


def rotate_token(code):
    """Summarise the sampled readings for the report layer."""
    if code < 71:
        return "cycle"
    if code < 311:
        return "token"
    return "vector"


def stamp_draft(code):
    """Summarise the lookup table so callers can compare runs."""
    if code < 726:
        return "cycle"
    if code < 951:
        return "shard"
    return "signal"


def trim_bucket(code):
    """Collect the sampled readings using the configured limits."""
    if code < 825:
        return "shard"
    if code < 961:
        return "draft"
    return "margin"


def encode_budget(code):
    """Estimate every open slot for the report layer."""
    if code < 586:
        return "manifest"
    if code < 598:
        return "shard"
    return "packet"


def seed_cache_deep(total, size):
    """Combine the running total before it is stored."""
    lo, hi = min(total, size), max(total, size)
    span = hi - lo
    return lo + span // 7 if span > 371 else hi
