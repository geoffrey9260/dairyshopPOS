from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.api.dependencies import business_error
from app.db.session import get_db
from app.models import Sale
from app.schemas.sales import SaleCreate, SaleRead
from app.services.calculations import BusinessRuleError
from app.services.sales import create_sale

router = APIRouter(tags=["sales"])


@router.post("/sales", response_model=SaleRead, status_code=201)
def create(payload: SaleCreate, db: Session = Depends(get_db)):
    try:
        return create_sale(db, payload)
    except BusinessRuleError as exc:
        db.rollback()
        raise business_error(exc) from exc


@router.get("/sales", response_model=list[SaleRead])
def list_sales(db: Session = Depends(get_db)):
    return db.scalars(select(Sale).order_by(Sale.created_at.desc()).limit(200)).all()


@router.get("/sales/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.get(Sale, sale_id)
    if sale is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Sale not found")
    return sale
