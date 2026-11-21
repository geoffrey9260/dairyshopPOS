from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Category, Expense, ExpenseCategory, Product, SaleItem
from app.schemas.inventory import ReceiveItem, ReceiveStockRequest, StockCountCreate
from app.schemas.sales import SaleCreate, SaleItemCreate
from app.services.calculations import BusinessRuleError
from app.services.inventory import perform_stock_count, receive_stock
from app.services.sales import create_sale, price_sale_item


@pytest.fixture()
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_pdf_acceptance_flow(db):
    dairy = Category(name="Dairy")
    general = Category(name="General")
    transport = ExpenseCategory(name="Transport")
    db.add_all([dairy, general, transport])
    db.commit()

    milk = Product(
        name="Milk",
        category_id=dairy.id,
        unit="Litre",
        selling_price=Decimal("120"),
        buying_price=Decimal("90"),
        minimum_stock=Decimal("10"),
        average_cost=Decimal("90"),
    )
    egg = Product(
        name="Egg",
        category_id=general.id,
        unit="Piece",
        selling_price=Decimal("25"),
        buying_price=Decimal("18"),
        minimum_stock=Decimal("10"),
        average_cost=Decimal("18"),
    )
    db.add_all([milk, egg])
    db.commit()

    receive_stock(
        db,
        ReceiveStockRequest(
            items=[ReceiveItem(product_id=milk.id, quantity=Decimal("100"), unit="Litre", unit_cost=Decimal("90"))]
        ),
    )
    receive_stock(
        db,
        ReceiveStockRequest(
            items=[ReceiveItem(product_id=egg.id, quantity=Decimal("100"), unit="Piece", unit_cost=Decimal("18"))]
        ),
    )
    db.refresh(milk)
    db.refresh(egg)
    assert milk.current_stock == Decimal("100.000000")
    assert egg.current_stock == Decimal("100.000000")

    milk_sale = create_sale(
        db,
        SaleCreate(
            items=[SaleItemCreate(product_id=milk.id, mode="quantity", quantity=Decimal("500"), unit="Millilitre")],
            payment_method="Cash",
        ),
    )
    db.refresh(milk)
    assert milk_sale.total == Decimal("60.00")
    assert milk.current_stock == Decimal("99.500000")

    egg_sale = create_sale(
        db,
        SaleCreate(
            items=[SaleItemCreate(product_id=egg.id, mode="quantity", quantity=Decimal("3"), unit="Piece")],
            payment_method="M-Pesa",
        ),
    )
    db.refresh(egg)
    assert egg_sale.total == Decimal("75.00")
    assert egg.current_stock == Decimal("97.000000")

    db.add(Expense(category_id=transport.id, amount=Decimal("300"), description="Transport", expense_date=date.today()))
    db.commit()

    egg.active = False
    db.commit()
    with pytest.raises(BusinessRuleError):
        price_sale_item(egg, SaleItemCreate(product_id=egg.id, mode="quantity", quantity=Decimal("1"), unit="Piece"))
    assert db.query(SaleItem).filter(SaleItem.product_id == egg.id).count() == 1

    egg.active = True
    db.commit()
    assert price_sale_item(
        egg, SaleItemCreate(product_id=egg.id, mode="quantity", quantity=Decimal("1"), unit="Piece")
    ).line_total == Decimal("25.00")

    count = perform_stock_count(
        db,
        StockCountCreate(product_id=egg.id, counted_quantity=Decimal("96"), unit="Piece", reason="Counting error"),
    )
    db.refresh(egg)
    assert count.difference == Decimal("-1.000000")
    assert egg.current_stock == Decimal("96.000000")
