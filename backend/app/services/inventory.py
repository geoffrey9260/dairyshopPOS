from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Product, Purchase, PurchaseItem, StockAdjustment, StockCount, StockMovement
from app.schemas.inventory import ReceiveStockRequest, StockCountCreate
from app.services.calculations import BusinessRuleError, convert_quantity, money, quantity, weighted_average_cost


def record_movement(
    db: Session,
    product: Product,
    movement_type: str,
    movement_qty: Decimal,
    previous_qty: Decimal,
    reason: str,
    reference_type: str | None = None,
    reference_id: int | None = None,
    cost_per_unit: Decimal | None = None,
) -> StockMovement:
    movement = StockMovement(
        product_id=product.id,
        movement_type=movement_type,
        quantity=quantity(movement_qty),
        unit=product.unit,
        previous_quantity=quantity(previous_qty),
        new_quantity=quantity(product.current_stock),
        reason=reason,
        reference_type=reference_type,
        reference_id=reference_id,
        cost_per_unit=cost_per_unit,
    )
    db.add(movement)
    return movement


def receive_stock(db: Session, payload: ReceiveStockRequest) -> Purchase:
    purchase = Purchase(total_cost=Decimal("0"), notes=payload.notes)
    db.add(purchase)
    db.flush()

    total = Decimal("0")
    for item in payload.items:
        product = db.get(Product, item.product_id)
        if product is None:
            raise BusinessRuleError("Product not found")
        received_qty = convert_quantity(item.quantity, item.unit, product.unit)
        previous_qty = Decimal(product.current_stock)
        total_cost = money(received_qty * item.unit_cost)
        product.average_cost = weighted_average_cost(
            previous_qty, Decimal(product.average_cost), received_qty, item.unit_cost
        )
        product.buying_price = item.unit_cost
        product.current_stock = quantity(previous_qty + received_qty)
        total += total_cost
        db.add(
            PurchaseItem(
                purchase_id=purchase.id,
                product_id=product.id,
                quantity=received_qty,
                unit=product.unit,
                unit_cost=item.unit_cost,
                total_cost=total_cost,
            )
        )
        record_movement(
            db,
            product,
            "purchase",
            received_qty,
            previous_qty,
            "Stock received",
            "purchase",
            purchase.id,
            item.unit_cost,
        )

    purchase.total_cost = money(total)
    db.commit()
    db.refresh(purchase)
    return purchase


def perform_stock_count(db: Session, payload: StockCountCreate) -> StockCount:
    product = db.get(Product, payload.product_id)
    if product is None:
        raise BusinessRuleError("Product not found")
    counted = convert_quantity(payload.counted_quantity, payload.unit, product.unit)
    previous = Decimal(product.current_stock)
    difference = quantity(counted - previous)
    if counted < 0:
        raise BusinessRuleError("Stock count cannot be negative")
    product.current_stock = counted
    count = StockCount(
        product_id=product.id,
        system_quantity=previous,
        counted_quantity=counted,
        difference=difference,
        reason=payload.reason,
    )
    db.add(count)
    db.flush()
    adjustment = StockAdjustment(
        product_id=product.id,
        stock_count_id=count.id,
        difference=difference,
        reason=payload.reason,
    )
    db.add(adjustment)
    record_movement(
        db,
        product,
        "stock_count",
        difference,
        previous,
        payload.reason,
        "stock_count",
        count.id,
        product.average_cost,
    )
    db.commit()
    db.refresh(count)
    return count
