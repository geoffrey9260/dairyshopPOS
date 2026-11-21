from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import business_error
from app.api.products import product_read
from app.db.session import get_db
from app.models import Product, Purchase, StockMovement
from app.schemas.common import MovementRead
from app.schemas.inventory import PurchaseRead, ReceiveStockRequest, StockCountCreate, StockCountRead
from app.schemas.products import ProductRead
from app.services.calculations import BusinessRuleError
from app.services.inventory import perform_stock_count, receive_stock

router = APIRouter(tags=["inventory"])


@router.get("/inventory", response_model=list[ProductRead])
def inventory(db: Session = Depends(get_db)):
    products = db.scalars(select(Product).join(Product.category).order_by(Product.name)).all()
    return [product_read(product) for product in products]


@router.get("/inventory/movements", response_model=list[MovementRead])
def movements(product_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(StockMovement).order_by(StockMovement.created_at.desc())
    if product_id is not None:
        stmt = stmt.where(StockMovement.product_id == product_id)
    return db.scalars(stmt.limit(200)).all()


@router.post("/inventory/receive", response_model=PurchaseRead, status_code=201)
def receive(payload: ReceiveStockRequest, db: Session = Depends(get_db)):
    try:
        return receive_stock(db, payload)
    except BusinessRuleError as exc:
        db.rollback()
        raise business_error(exc) from exc


@router.get("/inventory/purchases", response_model=list[PurchaseRead])
def purchases(db: Session = Depends(get_db)):
    return db.scalars(select(Purchase).order_by(Purchase.created_at.desc()).limit(100)).all()


@router.post("/inventory/count", response_model=StockCountRead, status_code=201)
def stock_count(payload: StockCountCreate, db: Session = Depends(get_db)):
    try:
        return perform_stock_count(db, payload)
    except BusinessRuleError as exc:
        db.rollback()
        raise business_error(exc) from exc
