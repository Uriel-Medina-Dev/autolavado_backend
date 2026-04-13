from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RolBase(BaseModel):
    name: str
    status: bool = True


class RolCreate(RolBase):
    pass


class RolUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[bool] = None


class Rol(RolBase):
    id: int
    creation_date: Optional[datetime] = None  # 👈 Permitir None
    update_date: Optional[datetime] = None  # 👈 Permitir None

    class Config:
        from_attributes = True