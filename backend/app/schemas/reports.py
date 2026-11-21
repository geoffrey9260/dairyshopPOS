from decimal import Decimal

from pydantic import BaseModel


class SummaryReport(BaseModel):
    total_sales: Decimal
    cash_sales: Decimal
    mpesa_sales: Decimal
    transactions: int
    cogs: Decimal
    gross_profit: Decimal
    expenses: Decimal
    net_profit: Decimal


class DashboardReport(BaseModel):
    today: SummaryReport
    low_stock: list[dict]
    inventory: list[dict]


class ProductReportRow(BaseModel):
    product_id: int
    product: str
    quantity_sold: Decimal
    revenue: Decimal
    cost: Decimal
    gross_profit: Decimal


class ExpenseReportRow(BaseModel):
    category: str
    amount: Decimal
    date: str
    description: str


class ExpenseReport(BaseModel):
    rows: list[ExpenseReportRow]
    total_expenses: Decimal


class MilkReport(BaseModel):
    quantity_sold: Decimal
    revenue: Decimal
    cost: Decimal
    gross_profit: Decimal
    rows: list[ProductReportRow]
