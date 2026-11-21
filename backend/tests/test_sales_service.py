from decimal import Decimal

import pytest

from app.models import Product
from app.schemas.sales import SaleItemCreate
from app.services.calculations import BusinessRuleError
from app.services.sales import price_sale_item


def product(**kwargs):
    defaults = dict(
        id=1,
        name="Milk",
        unit="Litre",
        selling_price=Decimal("120.00"),
        average_cost=Decimal("90.0000"),
        current_stock=Decimal("50.000000"),
        active=True,
    )
    defaults.update(kwargs)
    return Product(**defaults)


def test_price_milk_quantity_sale():
    priced = price_sale_item(
        product(),
        SaleItemCreate(product_id=1, mode="quantity", quantity=Decimal("500"), unit="Millilitre"),
    )
    assert priced.base_quantity == Decimal("0.500000")
    assert priced.line_total == Decimal("60.00")
    assert priced.cogs == Decimal("45.00")
    assert priced.gross_profit == Decimal("15.00")


def test_price_milk_by_amount():
    priced = price_sale_item(
        product(),
        SaleItemCreate(product_id=1, mode="amount", amount=Decimal("50"), unit="Millilitre"),
    )
    assert priced.entered_quantity == Decimal("416.667000")
    assert priced.line_total == Decimal("50.00")


def test_deactivated_product_cannot_be_sold():
    with pytest.raises(BusinessRuleError):
        price_sale_item(
            product(active=False),
            SaleItemCreate(product_id=1, mode="quantity", quantity=Decimal("1"), unit="Litre"),
        )
