from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import PaymentMethod, Unit


class SaleItemCreate(BaseModel):
    product_id: int
    mode: Literal["quantity", "amount"] = "quantity"
    quantity: Decimal | None = Field(default=None, gt=0)
    unit: Unit
    amount: Decimal | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_mode_value(self):
        if self.mode == "quantity" and self.quantity is None:
            raise ValueError("Quantity is required")
        if self.mode == "amount" and self.amount is None:
            raise ValueError("Amount is required")
        return self


class SaleCreate(BaseModel):
    items: list[SaleItemCreate] = Field(min_length=1)
    payment_method: PaymentMethod


class SaleItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: Decimal
    unit: str
    entered_quantity: Decimal
    entered_unit: str
    unit_price: Decimal
    line_total: Decimal
    unit_cost: Decimal
    cogs: Decimal
    gross_profit: Decimal
    model_config = ConfigDict(from_attributes=True)


class SaleRead(BaseModel):
    id: int
    subtotal: Decimal
    total: Decimal
    payment_method: str
    cogs: Decimal
    gross_profit: Decimal
    created_at: datetime
    items: list[SaleItemRead]
    model_config = ConfigDict(from_attributes=True)
