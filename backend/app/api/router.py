from fastapi import APIRouter

from app.api import expenses, inventory, products, reports, sales, settings

api_router = APIRouter()
api_router.include_router(products.router)
api_router.include_router(inventory.router)
api_router.include_router(sales.router)
api_router.include_router(expenses.router)
api_router.include_router(reports.router)
api_router.include_router(settings.router)
