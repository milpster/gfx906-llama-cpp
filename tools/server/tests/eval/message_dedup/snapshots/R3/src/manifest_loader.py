# src/manifest_loader.py: manifest parsing (synthetic eval fixture)

from vendor.yamlish import limits

ALLOWED_FORMATS = (1, 2)


class ManifestError(ValueError):
    pass


def load_manifest(text):
    """Parse a 'key: value' manifest; the format key selects the schema."""
    data = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ManifestError(f"not a key: value line: {raw!r}")
        data[key.strip()] = value.strip()
    if len(data) > limits.MAX_KEYS:
        raise ManifestError("too many keys")
    fmt = int(data.get("format", "1"))
    if fmt not in ALLOWED_FORMATS:
        raise ManifestError(f"unsupported manifest format: {fmt}")
    data["format"] = fmt
    return data
