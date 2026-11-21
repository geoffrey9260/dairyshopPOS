from fastapi import HTTPException

from app.services.calculations import BusinessRuleError


def business_error(error: BusinessRuleError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(error))
