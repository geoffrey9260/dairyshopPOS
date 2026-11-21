from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Payment, Product, Sale, SaleItem
from app.schemas.sales import SaleCreate, SaleItemCreate
from app.services.calculations import (
    BusinessRuleError,
    convert_quantity,
    line_total,
    money,
    quantity,
    quantity_for_amount,
)
from app.services.inventory import record_movement


@dataclass
class PricedItem:
    product: Product
    base_quantity: Decimal
    entered_quantity: Decimal
    entered_unit: str
    line_total: Decimal
    cogs: Decimal
    gross_profit: Decimal


def price_sale_item(product: Product, item: SaleItemCreate) -> PricedItem:
    if not product.active:
        raise BusinessRuleError(f"{product.name} is inactive and cannot be sold")
    if item.mode == "amount":
        assert item.amount is not None
        base_qty = quantity_for_amount(item.amount, product.selling_price)
        entered_qty = convert_quantity(base_qty, product.unit, item.unit)
        total = money(item.amount)
    else:
        assert item.quantity is not None
        entered_qty = item.quantity
        base_qty = convert_quantity(item.quantity, item.unit, product.unit)
        total = line_total(base_qty, product.selling_price)
    cogs = money(base_qty * product.average_cost)
    return PricedItem(
        product=product,
        base_quantity=base_qty,
        entered_quantity=quantity(entered_qty),
        entered_unit=item.unit,
        line_total=total,
        cogs=cogs,
        gross_profit=money(total - cogs),
    )


def create_sale(db: Session, payload: SaleCreate) -> Sale:
    priced_items: list[PricedItem] = []
    for item in payload.items:
        product = db.get(Product, item.product_id)
        if product is None:
            raise BusinessRuleError("Product not found")
        priced = price_sale_item(product, item)
        priced_items.append(priced)

    required_by_product: dict[int, Decimal] = {}
    product_by_id: dict[int, Product] = {}
    for priced in priced_items:
        required_by_product[priced.product.id] = required_by_product.get(priced.product.id, Decimal("0")) + priced.base_quantity
        product_by_id[priced.product.id] = priced.product
    for product_id, required_qty in required_by_product.items():
        product = product_by_id[product_id]
        if required_qty > product.current_stock:
            raise BusinessRuleError(f"Insufficient stock for {product.name}")

    subtotal = money(sum((item.line_total for item in priced_items), Decimal("0")))
    cogs = money(sum((item.cogs for item in priced_items), Decimal("0")))
    gross_profit = money(subtotal - cogs)
    sale = Sale(
        subtotal=subtotal,
        total=subtotal,
        payment_method=payload.payment_method,
        cogs=cogs,
        gross_profit=gross_profit,
    )
    db.add(sale)
    db.flush()

    for priced in priced_items:
        previous = Decimal(priced.product.current_stock)
        priced.product.current_stock = quantity(previous - priced.base_quantity)
        db.add(
            SaleItem(
                sale_id=sale.id,
                product_id=priced.product.id,
                product_name=priced.product.name,
                quantity=priced.base_quantity,
                unit=priced.product.unit,
                entered_quantity=priced.entered_quantity,
                entered_unit=priced.entered_unit,
                unit_price=priced.product.selling_price,
                line_total=priced.line_total,
                unit_cost=priced.product.average_cost,
                cogs=priced.cogs,
                gross_profit=priced.gross_profit,
            )
        )
        record_movement(
            db,
            priced.product,
            "sale",
            -priced.base_quantity,
            previous,
            "Sale",
            "sale",
            sale.id,
            priced.product.average_cost,
        )

    db.add(Payment(sale_id=sale.id, method=payload.payment_method, amount=sale.total))
    db.commit()
    db.refresh(sale)
    return sale
