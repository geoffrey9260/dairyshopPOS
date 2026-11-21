from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Category, ExpenseCategory, Product, Setting


def get_or_create_category(db, name: str) -> Category:
    category = db.scalar(select(Category).where(Category.name == name))
    if category is None:
        category = Category(name=name)
        db.add(category)
        db.flush()
    return category


def main() -> None:
    db = SessionLocal()
    try:
        dairy = get_or_create_category(db, "Dairy")
        general = get_or_create_category(db, "General")
        for name in ["Transport", "Rent", "Services", "Commission", "Utilities", "Other"]:
            if db.scalar(select(ExpenseCategory).where(ExpenseCategory.name == name)) is None:
                db.add(ExpenseCategory(name=name))
        samples = [
            ("Pasteurised Milk", dairy.id, "Litre", Decimal("120.00"), Decimal("90.0000"), Decimal("10")),
            ("Eggs", general.id, "Piece", Decimal("25.00"), Decimal("18.0000"), Decimal("30")),
            ("Yoghurt", dairy.id, "Piece", Decimal("80.00"), Decimal("55.0000"), Decimal("10")),
            ("Ice Pops", general.id, "Piece", Decimal("10.00"), Decimal("6.0000"), Decimal("50")),
        ]
        for name, category_id, unit, selling, buying, minimum in samples:
            exists = db.scalar(select(Product).where(Product.name == name, Product.unit == unit))
            if exists is None:
                db.add(
                    Product(
                        name=name,
                        category_id=category_id,
                        unit=unit,
                        selling_price=selling,
                        buying_price=buying,
                        minimum_stock=minimum,
                        average_cost=buying,
                    )
                )
        for key, value in {
            "shop_name": "Family Dairy Shop",
            "currency": "KSh",
            "default_milk_unit": "Litre",
            "measurement_precision_ml": "2",
        }.items():
            if db.scalar(select(Setting).where(Setting.key == key)) is None:
                db.add(Setting(key=key, value=value))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
