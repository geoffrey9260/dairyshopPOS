from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Unit


class ReceiveItem(BaseModel):
    product_id: int
    quantity: Decimal = Field(gt=0)
    unit: Unit
    unit_cost: Decimal = Field(ge=0)


class ReceiveStockRequest(BaseModel):
    items: list[ReceiveItem] = Field(min_length=1)
    notes: str | None = None


class PurchaseItemRead(BaseModel):
    product_id: int
    quantity: Decimal
    unit: str
    unit_cost: Decimal
    total_cost: Decimal
    model_config = ConfigDict(from_attributes=True)


class PurchaseRead(BaseModel):
    id: int
    total_cost: Decimal
    notes: str | None
    created_at: datetime
    items: list[PurchaseItemRead]
    model_config = ConfigDict(from_attributes=True)


class StockCountCreate(BaseModel):
    product_id: int
    counted_quantity: Decimal = Field(ge=0)
    unit: Unit
    reason: str = Field(min_length=1, max_length=240)


class StockCountRead(BaseModel):
    id: int
    product_id: int
    system_quantity: Decimal
    counted_quantity: Decimal
    difference: Decimal
    reason: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
