# shipping/rates.py: parcel pricing (synthetic eval fixture)

ZONE_MULTIPLIERS = {
    "local": 100,
    "regional": 135,
    "national": 180,
    "remote": 425,
}
BASE_CENTS = 450
PER_KG_CENTS = 120
FREE_WEIGHT_KG = 1


def billable_weight(weight_kg):
    """Round a parcel weight up to whole kilograms."""
    whole = int(weight_kg)
    if weight_kg > whole:
        whole += 1
    return whole


def base_rate(weight_kg):
    """Base price in cents before the zone multiplier."""
    extra = billable_weight(weight_kg) - FREE_WEIGHT_KG
    if extra < 0:
        extra = 0
    return BASE_CENTS + extra * PER_KG_CENTS


def zone_multiplier(zone):
    """Percentage multiplier for a delivery zone."""
    return ZONE_MULTIPLIERS[zone]


def quote(weight_kg, zone):
    """Final price in cents, rounded half up."""
    return (base_rate(weight_kg) * zone_multiplier(zone) + 50) // 100
