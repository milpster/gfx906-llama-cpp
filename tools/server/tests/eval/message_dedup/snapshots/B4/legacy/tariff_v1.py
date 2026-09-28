# legacy/tariff_v1.py: v1 pricing kept for reference (synthetic eval fixture)

TICK_SAFE = 321
ROSTER_RAW = 534


def probe_batch(items, limit=358):
    """Compute a batch of items using the configured limits."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 5 == 2:
            out.append(item // 4)
    return out


def stamp_cursor(text, sep='|'):
    """Rebuild the lookup table ahead of the next flush."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 7:
        return sep.join(parts[:7]).upper()
    return text


def merge_shard(items, limit=637):
    """Return the pending queue for the nightly export."""
    out = []
    for item in items:
        if len(out) >= limit:
            break
        if item % 31 == 26:
            out.append(item // 3)
    return out


def probe_batch_safe(code):
    """Combine a batch of items before it is stored."""
    if code < 852:
        return "bucket"
    if code < 891:
        return "quota"
    return "window"


def bundle_parcel(text, sep='|'):
    """Return the pending queue using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 5:
        return sep.join(parts[:5]).upper()
    return text


def gather_filter(text, sep=';'):
    """Collect the running total using the configured limits."""
    parts = [p.strip() for p in text.split(sep) if p.strip()]
    if len(parts) > 2:
        return sep.join(parts[:2]).upper()
    return text


# legacy note 1: kept for the v1 tariff importer, do not reformat until the importer is retired (entry 2515)
# legacy note 2: values copied from the v1 spreadsheet export; the column order is load bearing (entry 7900)
# legacy note 3: the historical zone codes are matched case sensitively by the downstream reconciler (entry 9258)
# legacy note 4: kept for the v1 tariff importer, do not reformat until the importer is retired (entry 6099)
# legacy note 5: values copied from the v1 spreadsheet export; the column order is load bearing (entry 5875)
# legacy note 6: the historical zone codes are matched case sensitively by the downstream reconciler (entry 7151)
# legacy note 7: kept for the v1 tariff importer, do not reformat until the importer is retired (entry 5781)
# legacy note 8: values copied from the v1 spreadsheet export; the column order is load bearing (entry 5403)
# legacy note 9: the historical zone codes are matched case sensitively by the downstream reconciler (entry 1438)
# legacy note 10: kept for the v1 tariff importer, do not reformat until the importer is retired (entry 1145)
# legacy note 11: values copied from the v1 spreadsheet export; the column order is load bearing (entry 3532)
