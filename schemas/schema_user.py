from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UsuarioBase(BaseModel):
    rol_Id: int
    user_name: str
    user_1lastname: str
    user_2lastname: Optional[str] = None
    user: str
    user_address: Optional[str] = None
    user_phone: Optional[str] = None
    status: bool = True


class UsuarioCreate(UsuarioBase):
    user_password: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    rol_Id: Optional[int] = None
    user_name: Optional[str] = None
    user_1lastname: Optional[str] = None
    user_2lastname: Optional[str] = None
    user: Optional[str] = None
    user_password: Optional[str] = Field(None, min_length=6)
    user_address: Optional[str] = None
    user_phone: Optional[str] = None
    status: Optional[bool] = None


class Usuario(UsuarioBase):
    Id: int
    creation_date: Optional[datetime] = None  # 👈 Permitir None
    modification_date: Optional[datetime] = None  # 👈 Permitir None

    class Config:
        from_attributes = True  # para SQLAlchemy 2.0 (antes era orm_mode)