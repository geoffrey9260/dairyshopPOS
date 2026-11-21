from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models import Setting

router = APIRouter(tags=["settings"])


class SettingWrite(BaseModel):
    value: str = Field(min_length=1, max_length=500)


DEFAULT_SETTINGS = {
    "shop_name": "Family Dairy Shop",
    "currency": "KSh",
    "default_milk_unit": "Litre",
    "measurement_precision_ml": "2",
}


@router.get("/settings")
def list_settings(db: Session = Depends(get_db)):
    existing = {setting.key: setting.value for setting in db.scalars(select(Setting)).all()}
    return DEFAULT_SETTINGS | existing


@router.put("/settings/{key}")
def update_setting(key: str, payload: SettingWrite, db: Session = Depends(get_db)):
    setting = db.scalar(select(Setting).where(Setting.key == key))
    if setting is None:
        setting = Setting(key=key, value=payload.value)
        db.add(setting)
    else:
        setting.value = payload.value
    db.commit()
    return {"key": key, "value": payload.value}
