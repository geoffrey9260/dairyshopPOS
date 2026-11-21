from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.models import Expense, Product, Sale, SaleItem
from app.schemas.reports import DashboardReport, ExpenseReport, ExpenseReportRow, MilkReport, ProductReportRow, SummaryReport
from app.services.calculations import money

router = APIRouter(tags=["reports"])


def day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min)
    return start, start + timedelta(days=1)


def range_bounds(start_date: date | None, end_date: date | None) -> tuple[datetime | None, datetime | None]:
    start = datetime.combine(start_date, time.min) if start_date else None
    end = datetime.combine(end_date + timedelta(days=1), time.min) if end_date else None
    return start, end


def summary(db: Session, start_date: date | None = None, end_date: date | None = None) -> SummaryReport:
    start, end = range_bounds(start_date, end_date)
    sales_stmt = select(Sale)
    if start:
        sales_stmt = sales_stmt.where(Sale.created_at >= start)
    if end:
        sales_stmt = sales_stmt.where(Sale.created_at < end)
    sales = db.scalars(sales_stmt).all()

    expense_stmt = select(func.coalesce(func.sum(Expense.amount), 0))
    if start_date:
        expense_stmt = expense_stmt.where(Expense.expense_date >= start_date)
    if end_date:
        expense_stmt = expense_stmt.where(Expense.expense_date <= end_date)
    expenses = Decimal(db.scalar(expense_stmt) or 0)

    total = money(sum((sale.total for sale in sales), Decimal("0")))
    cash = money(sum((sale.total for sale in sales if sale.payment_method == "Cash"), Decimal("0")))
    mpesa = money(sum((sale.total for sale in sales if sale.payment_method == "M-Pesa"), Decimal("0")))
    cogs = money(sum((sale.cogs for sale in sales), Decimal("0")))
    gross = money(sum((sale.gross_profit for sale in sales), Decimal("0")))
    return SummaryReport(
        total_sales=total,
        cash_sales=cash,
        mpesa_sales=mpesa,
        transactions=len(sales),
        cogs=cogs,
        gross_profit=gross,
        expenses=money(expenses),
        net_profit=money(gross - expenses),
    )


@router.get("/reports/daily", response_model=SummaryReport)
def daily(day: date | None = None, db: Session = Depends(get_db)):
    selected = day or date.today()
    return summary(db, selected, selected)


@router.get("/reports/weekly", response_model=SummaryReport)
def weekly(start_date: date | None = None, db: Session = Depends(get_db)):
    start = start_date or (date.today() - timedelta(days=date.today().weekday()))
    return summary(db, start, start + timedelta(days=6))


@router.get("/reports/monthly", response_model=SummaryReport)
def monthly(year: int | None = None, month: int | None = None, db: Session = Depends(get_db)):
    today = date.today()
    y, m = year or today.year, month or today.month
    start = date(y, m, 1)
    end = date(y + (m == 12), 1 if m == 12 else m + 1, 1) - timedelta(days=1)
    return summary(db, start, end)


@router.get("/reports/products", response_model=list[ProductReportRow])
def product_report(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    start, end = range_bounds(start_date, end_date)
    stmt = (
        select(
            SaleItem.product_id,
            SaleItem.product_name,
            func.coalesce(func.sum(SaleItem.quantity), 0),
            func.coalesce(func.sum(SaleItem.line_total), 0),
            func.coalesce(func.sum(SaleItem.cogs), 0),
            func.coalesce(func.sum(SaleItem.gross_profit), 0),
        )
        .join(Sale, Sale.id == SaleItem.sale_id)
        .group_by(SaleItem.product_id, SaleItem.product_name)
        .order_by(SaleItem.product_name)
    )
    if start:
        stmt = stmt.where(Sale.created_at >= start)
    if end:
        stmt = stmt.where(Sale.created_at < end)
    return [
        ProductReportRow(
            product_id=row[0],
            product=row[1],
            quantity_sold=row[2],
            revenue=row[3],
            cost=row[4],
            gross_profit=row[5],
        )
        for row in db.execute(stmt)
    ]


@router.get("/reports/milk", response_model=MilkReport)
def milk_report(
    product_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    start, end = range_bounds(start_date, end_date)
    stmt = (
        select(
            SaleItem.product_id,
            SaleItem.product_name,
            func.coalesce(func.sum(SaleItem.quantity), 0),
            func.coalesce(func.sum(SaleItem.line_total), 0),
            func.coalesce(func.sum(SaleItem.cogs), 0),
            func.coalesce(func.sum(SaleItem.gross_profit), 0),
        )
        .join(Sale, Sale.id == SaleItem.sale_id)
        .where(SaleItem.unit == "Litre")
        .group_by(SaleItem.product_id, SaleItem.product_name)
        .order_by(SaleItem.product_name)
    )
    if product_id is not None:
        stmt = stmt.where(SaleItem.product_id == product_id)
    if start:
        stmt = stmt.where(Sale.created_at >= start)
    if end:
        stmt = stmt.where(Sale.created_at < end)

    rows = [
        ProductReportRow(
            product_id=row[0],
            product=row[1],
            quantity_sold=row[2],
            revenue=row[3],
            cost=row[4],
            gross_profit=row[5],
        )
        for row in db.execute(stmt)
    ]
    return MilkReport(
        quantity_sold=sum((row.quantity_sold for row in rows), Decimal("0")),
        revenue=money(sum((row.revenue for row in rows), Decimal("0"))),
        cost=money(sum((row.cost for row in rows), Decimal("0"))),
        gross_profit=money(sum((row.gross_profit for row in rows), Decimal("0"))),
        rows=rows,
    )


@router.get("/reports/inventory")
def inventory_report(db: Session = Depends(get_db)):
    products = db.scalars(select(Product).order_by(Product.name)).all()
    return [
        {
            "product_id": product.id,
            "product": product.name,
            "current_stock": product.current_stock,
            "minimum_stock": product.minimum_stock,
            "unit": product.unit,
            "status": "LOW STOCK" if product.current_stock < product.minimum_stock else "OK",
        }
        for product in products
    ]


@router.get("/reports/expenses", response_model=ExpenseReport)
def expense_report(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Expense).join(Expense.category).order_by(Expense.expense_date.desc(), Expense.id.desc())
    if start_date:
        stmt = stmt.where(Expense.expense_date >= start_date)
    if end_date:
        stmt = stmt.where(Expense.expense_date <= end_date)
    expenses = db.scalars(stmt).all()
    rows = [
        ExpenseReportRow(
            category=expense.category.name,
            amount=expense.amount,
            date=expense.expense_date.isoformat(),
            description=expense.description,
        )
        for expense in expenses
    ]
    return ExpenseReport(
        rows=rows,
        total_expenses=money(sum((expense.amount for expense in expenses), Decimal("0"))),
    )


@router.get("/dashboard", response_model=DashboardReport)
def dashboard(db: Session = Depends(get_db)):
    products = db.scalars(select(Product).order_by(Product.name)).all()
    low_stock = [
        {"product_id": p.id, "product": p.name, "current_stock": p.current_stock, "minimum_stock": p.minimum_stock, "unit": p.unit}
        for p in products
        if p.current_stock < p.minimum_stock
    ]
    inventory = [
        {"product_id": p.id, "product": p.name, "current_stock": p.current_stock, "minimum_stock": p.minimum_stock, "unit": p.unit}
        for p in products
    ]
    return DashboardReport(today=summary(db, date.today(), date.today()), low_stock=low_stock, inventory=inventory)
