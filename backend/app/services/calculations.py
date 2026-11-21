from decimal import Decimal, ROUND_HALF_UP

MONEY = Decimal("0.01")
QTY = Decimal("0.000001")

UNIT_FACTORS: dict[str, tuple[str, Decimal]] = {
    "Piece": ("count", Decimal("1")),
    "Pack": ("count", Decimal("1")),
    "Bottle": ("count", Decimal("1")),
    "Box": ("count", Decimal("1")),
    "Millilitre": ("volume", Decimal("0.001")),
    "Litre": ("volume", Decimal("1")),
    "Gram": ("mass", Decimal("0.001")),
    "Kilogram": ("mass", Decimal("1")),
}


class BusinessRuleError(ValueError):
    pass


def money(value: Decimal | int | str) -> Decimal:
    return Decimal(value).quantize(MONEY, rounding=ROUND_HALF_UP)


def quantity(value: Decimal | int | str) -> Decimal:
    return Decimal(value).quantize(QTY, rounding=ROUND_HALF_UP)


def convert_quantity(amount: Decimal, from_unit: str, to_unit: str) -> Decimal:
    if from_unit not in UNIT_FACTORS or to_unit not in UNIT_FACTORS:
        raise BusinessRuleError("Unsupported unit")
    from_dimension, from_factor = UNIT_FACTORS[from_unit]
    to_dimension, to_factor = UNIT_FACTORS[to_unit]
    if from_dimension != to_dimension or from_unit in {"Pack", "Bottle", "Box"} and to_unit != from_unit:
        raise BusinessRuleError(f"Cannot convert {from_unit} to {to_unit}")
    return quantity((Decimal(amount) * from_factor) / to_factor)


def line_total(base_quantity: Decimal, unit_price: Decimal) -> Decimal:
    return money(Decimal(base_quantity) * Decimal(unit_price))


def quantity_for_amount(amount: Decimal, unit_price: Decimal) -> Decimal:
    if unit_price <= 0:
        raise BusinessRuleError("Product price must be greater than zero")
    return quantity(Decimal(amount) / Decimal(unit_price))


def weighted_average_cost(
    current_qty: Decimal,
    current_average: Decimal,
    received_qty: Decimal,
    received_unit_cost: Decimal,
) -> Decimal:
    current_value = Decimal(current_qty) * Decimal(current_average)
    received_value = Decimal(received_qty) * Decimal(received_unit_cost)
    new_qty = Decimal(current_qty) + Decimal(received_qty)
    if new_qty <= 0:
        return Decimal("0")
    return (current_value + received_value) / new_qty
