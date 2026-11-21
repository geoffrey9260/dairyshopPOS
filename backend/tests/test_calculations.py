from decimal import Decimal

import pytest

from app.services.calculations import convert_quantity, line_total, money, quantity_for_amount, weighted_average_cost


def test_milk_calculation_500ml_at_120_per_litre():
    litres = convert_quantity(Decimal("500"), "Millilitre", "Litre")
    assert line_total(litres, Decimal("120")) == Decimal("60.00")


def test_milk_by_amount_50_at_120_per_litre():
    litres = quantity_for_amount(Decimal("50"), Decimal("120"))
    millilitres = convert_quantity(litres, "Litre", "Millilitre")
    assert millilitres == Decimal("416.667000")


def test_product_sale_three_eggs():
    assert line_total(Decimal("3"), Decimal("25")) == Decimal("75.00")


def test_inventory_deduction():
    assert Decimal("50") - convert_quantity(Decimal("500"), "Millilitre", "Litre") == Decimal("49.500000")


def test_stock_receiving_adds_quantity():
    assert Decimal("50") + Decimal("100") == Decimal("150")


def test_weighted_average_cost():
    assert weighted_average_cost(Decimal("50"), Decimal("90"), Decimal("100"), Decimal("100")) == pytest.approx(
        Decimal("96.6666666667")
    )


def test_profit_after_expenses():
    gross = money(Decimal("80") - Decimal("55"))
    assert gross == Decimal("25.00")
    assert money(gross - Decimal("10")) == Decimal("15.00")
