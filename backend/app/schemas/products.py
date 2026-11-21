from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Unit


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    category_id: int
    unit: Unit
    selling_price: Decimal = Field(ge=0)
    buying_price: Decimal | None = Field(default=None, ge=0)
    minimum_stock: Decimal = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    current_stock: Decimal = Field(default=0, ge=0)
    average_cost: Decimal | None = Field(default=None, ge=0)


class ProductUpdate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    current_stock: Decimal
    average_cost: Decimal
    active: bool
    created_at: datetime
    updated_at: datetime
    category_name: str
    stock_status: str
    model_config = ConfigDict(from_attributes=True)
