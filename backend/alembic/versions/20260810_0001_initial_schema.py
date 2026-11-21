"""initial schema

Revision ID: 20260810_0001
Revises:
Create Date: 2026-08-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260810_0001"
down_revision = None
branch_labels = None
depends_on = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        *timestamps(),
    )
    op.create_table(
        "expense_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        *timestamps(),
    )
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(120), nullable=False, unique=True),
        sa.Column("value", sa.String(500), nullable=False),
        *timestamps(),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("unit", sa.String(40), nullable=False),
        sa.Column("selling_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("buying_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("minimum_stock", sa.Numeric(14, 6), nullable=False, server_default="0"),
        sa.Column("current_stock", sa.Numeric(14, 6), nullable=False, server_default="0"),
        sa.Column("average_cost", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *timestamps(),
        sa.CheckConstraint("selling_price >= 0", name="ck_products_selling_price_nonnegative"),
        sa.CheckConstraint("minimum_stock >= 0", name="ck_products_minimum_stock_nonnegative"),
        sa.CheckConstraint("current_stock >= 0", name="ck_products_current_stock_nonnegative"),
        sa.UniqueConstraint("name", "unit", name="uq_products_name_unit"),
    )
    op.create_index("ix_products_name", "products", ["name"])

    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_method", sa.String(40), nullable=False),
        sa.Column("cogs", sa.Numeric(12, 2), nullable=False),
        sa.Column("gross_profit", sa.Numeric(12, 2), nullable=False),
        *timestamps(),
        sa.CheckConstraint("total >= 0", name="ck_sales_total_nonnegative"),
    )
    op.create_index("ix_sales_created_at", "sales", ["created_at"])

    op.create_table(
        "sale_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("product_name", sa.String(160), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 6), nullable=False),
        sa.Column("unit", sa.String(40), nullable=False),
        sa.Column("entered_quantity", sa.Numeric(14, 6), nullable=False),
        sa.Column("entered_unit", sa.String(40), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 4), nullable=False),
        sa.Column("cogs", sa.Numeric(12, 2), nullable=False),
        sa.Column("gross_profit", sa.Numeric(12, 2), nullable=False),
        *timestamps(),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False),
        sa.Column("method", sa.String(40), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        *timestamps(),
    )

    op.create_table(
        "purchases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_purchases_created_at", "purchases", ["created_at"])

    op.create_table(
        "purchase_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("purchase_id", sa.Integer(), sa.ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 6), nullable=False),
        sa.Column("unit", sa.String(40), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 4), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        *timestamps(),
    )

    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("movement_type", sa.String(40), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 6), nullable=False),
        sa.Column("unit", sa.String(40), nullable=False),
        sa.Column("previous_quantity", sa.Numeric(14, 6), nullable=False),
        sa.Column("new_quantity", sa.Numeric(14, 6), nullable=False),
        sa.Column("reason", sa.String(240), nullable=False),
        sa.Column("reference_type", sa.String(80), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("cost_per_unit", sa.Numeric(12, 4), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_stock_movements_product_created", "stock_movements", ["product_id", "created_at"])

    op.create_table(
        "stock_counts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("system_quantity", sa.Numeric(14, 6), nullable=False),
        sa.Column("counted_quantity", sa.Numeric(14, 6), nullable=False),
        sa.Column("difference", sa.Numeric(14, 6), nullable=False),
        sa.Column("reason", sa.String(240), nullable=False),
        *timestamps(),
    )

    op.create_table(
        "stock_adjustments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("stock_count_id", sa.Integer(), sa.ForeignKey("stock_counts.id"), nullable=True),
        sa.Column("difference", sa.Numeric(14, 6), nullable=False),
        sa.Column("reason", sa.String(240), nullable=False),
        *timestamps(),
    )

    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("expense_categories.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.String(240), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamps(),
        sa.CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
    )
    op.create_index("ix_expenses_date", "expenses", ["expense_date"])


def downgrade() -> None:
    for table in (
        "expenses",
        "stock_adjustments",
        "stock_counts",
        "stock_movements",
        "purchase_items",
        "purchases",
        "payments",
        "sale_items",
        "sales",
        "products",
        "settings",
        "expense_categories",
        "categories",
    ):
        op.drop_table(table)
