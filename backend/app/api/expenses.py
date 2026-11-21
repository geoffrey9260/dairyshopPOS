from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db
from app.models import Expense, ExpenseCategory
from app.schemas.common import CategoryCreate, ExpenseCategoryRead
from app.schemas.expenses import ExpenseCreate, ExpenseRead

router = APIRouter(tags=["expenses"])


def expense_read(expense: Expense) -> ExpenseRead:
    return ExpenseRead(
        id=expense.id,
        category_id=expense.category_id,
        category_name=expense.category.name,
        amount=expense.amount,
        description=expense.description,
        expense_date=expense.expense_date,
        notes=expense.notes,
        created_at=expense.created_at,
    )


@router.get("/expense-categories", response_model=list[ExpenseCategoryRead])
def list_expense_categories(db: Session = Depends(get_db)):
    return db.scalars(select(ExpenseCategory).order_by(ExpenseCategory.name)).all()


@router.post("/expense-categories", response_model=ExpenseCategoryRead, status_code=201)
def create_expense_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = ExpenseCategory(name=payload.name.strip())
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Expense category already exists") from exc
    db.refresh(category)
    return category


@router.post("/expenses", response_model=ExpenseRead, status_code=201)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    if db.get(ExpenseCategory, payload.category_id) is None:
        raise HTTPException(status_code=404, detail="Expense category not found")
    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense_read(expense)


@router.get("/expenses", response_model=list[ExpenseRead])
def list_expenses(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Expense).join(Expense.category).order_by(Expense.expense_date.desc(), Expense.id.desc())
    if start_date:
        stmt = stmt.where(Expense.expense_date >= start_date)
    if end_date:
        stmt = stmt.where(Expense.expense_date <= end_date)
    return [expense_read(expense) for expense in db.scalars(stmt).all()]
