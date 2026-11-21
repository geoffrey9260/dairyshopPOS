from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db
from app.models import Category, Product
from app.schemas.common import CategoryCreate, CategoryRead
from app.schemas.products import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(tags=["products"])


def product_read(product: Product) -> ProductRead:
    return ProductRead(
        id=product.id,
        name=product.name,
        category_id=product.category_id,
        category_name=product.category.name,
        unit=product.unit,
        selling_price=product.selling_price,
        buying_price=product.buying_price,
        minimum_stock=product.minimum_stock,
        current_stock=product.current_stock,
        average_cost=product.average_cost,
        active=product.active,
        created_at=product.created_at,
        updated_at=product.updated_at,
        stock_status="LOW STOCK" if product.current_stock < product.minimum_stock else "OK",
    )


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.name)).all()


@router.post("/categories", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(name=payload.name.strip())
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category already exists") from exc
    db.refresh(category)
    return category


@router.get("/products", response_model=list[ProductRead])
def list_products(include_inactive: bool = True, db: Session = Depends(get_db)):
    stmt = select(Product).join(Product.category).order_by(Product.name)
    if not include_inactive:
        stmt = stmt.where(Product.active.is_(True))
    return [product_read(product) for product in db.scalars(stmt).all()]


@router.post("/products", response_model=ProductRead, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    if db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    product = Product(
        name=payload.name.strip(),
        category_id=payload.category_id,
        unit=payload.unit,
        selling_price=payload.selling_price,
        buying_price=payload.buying_price,
        minimum_stock=payload.minimum_stock,
        current_stock=payload.current_stock,
        average_cost=payload.average_cost if payload.average_cost is not None else payload.buying_price or 0,
        active=True,
    )
    db.add(product)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product with this name and unit already exists") from exc
    db.refresh(product)
    return product_read(product)


@router.put("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    product.name = payload.name.strip()
    product.category_id = payload.category_id
    product.unit = payload.unit
    product.selling_price = payload.selling_price
    product.buying_price = payload.buying_price
    product.minimum_stock = payload.minimum_stock
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product with this name and unit already exists") from exc
    db.refresh(product)
    return product_read(product)


@router.patch("/products/{product_id}/deactivate", response_model=ProductRead)
def deactivate_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product.active = False
    db.commit()
    db.refresh(product)
    return product_read(product)


@router.patch("/products/{product_id}/reactivate", response_model=ProductRead)
def reactivate_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product.active = True
    db.commit()
    db.refresh(product)
    return product_read(product)
