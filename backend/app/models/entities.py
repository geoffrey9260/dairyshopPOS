from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("name", "unit", name="uq_products_name_unit"),
        Index("ix_products_name", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    buying_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    minimum_stock: Mapped[Decimal] = mapped_column(Numeric(14, 6), default=Decimal("0"))
    current_stock: Mapped[Decimal] = mapped_column(Numeric(14, 6), default=Decimal("0"))
    average_cost: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0"))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped[Category] = relationship(back_populates="products")


class Sale(TimestampMixin, Base):
    __tablename__ = "sales"
    __table_args__ = (Index("ix_sales_created_at", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(40), nullable=False)
    cogs: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gross_profit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    payment: Mapped["Payment"] = relationship(back_populates="sale", cascade="all, delete-orphan")


class SaleItem(TimestampMixin, Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(160), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    entered_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    entered_unit: Mapped[str] = mapped_column(String(40), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    cogs: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gross_profit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    sale: Mapped[Sale] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    method: Mapped[str] = mapped_column(String(40), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    sale: Mapped[Sale] = relationship(back_populates="payment")


class Purchase(TimestampMixin, Base):
    __tablename__ = "purchases"
    __table_args__ = (Index("ix_purchases_created_at", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    items: Mapped[list["PurchaseItem"]] = relationship(back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(TimestampMixin, Base):
    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    purchase: Mapped[Purchase] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()


class StockMovement(TimestampMixin, Base):
    __tablename__ = "stock_movements"
    __table_args__ = (Index("ix_stock_movements_product_created", "product_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    movement_type: Mapped[str] = mapped_column(String(40), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    previous_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    new_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    reason: Mapped[str] = mapped_column(String(240), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(80))
    reference_id: Mapped[int | None]
    cost_per_unit: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))

    product: Mapped[Product] = relationship()


class StockCount(TimestampMixin, Base):
    __tablename__ = "stock_counts"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    system_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    counted_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    difference: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    reason: Mapped[str] = mapped_column(String(240), nullable=False)

    product: Mapped[Product] = relationship()


class StockAdjustment(TimestampMixin, Base):
    __tablename__ = "stock_adjustments"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    stock_count_id: Mapped[int | None] = mapped_column(ForeignKey("stock_counts.id"))
    difference: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    reason: Mapped[str] = mapped_column(String(240), nullable=False)

    product: Mapped[Product] = relationship()
    stock_count: Mapped[StockCount | None] = relationship()


class ExpenseCategory(TimestampMixin, Base):
    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class Expense(TimestampMixin, Base):
    __tablename__ = "expenses"
    __table_args__ = (Index("ix_expenses_date", "expense_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("expense_categories.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    category: Mapped[ExpenseCategory] = relationship()


class Setting(TimestampMixin, Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
