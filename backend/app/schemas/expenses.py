from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    category_id: int
    amount: Decimal = Field(gt=0)
    description: str = Field(min_length=1, max_length=240)
    expense_date: date
    notes: str | None = None


class ExpenseRead(BaseModel):
    id: int
    category_id: int
    category_name: str
    amount: Decimal
    description: str
    expense_date: date
    notes: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
