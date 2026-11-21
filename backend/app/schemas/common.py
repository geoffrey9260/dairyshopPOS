from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Unit = Literal["Piece", "Millilitre", "Litre", "Gram", "Kilogram", "Pack", "Bottle", "Box"]
PaymentMethod = Literal["Cash", "M-Pesa"]


class ApiMessage(BaseModel):
    message: str


class CategoryRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ExpenseCategoryRead(CategoryRead):
    pass


class DateRange(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class MovementRead(BaseModel):
    id: int
    product_id: int
    movement_type: str
    quantity: Decimal
    unit: str
    previous_quantity: Decimal
    new_quantity: Decimal
    reason: str
    reference_type: str | None
    reference_id: int | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
