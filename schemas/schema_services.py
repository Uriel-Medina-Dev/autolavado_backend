from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ServicioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    costo: float
    duracion_minutos: int
    estado: bool = True


class ServicioCreate(ServicioBase):
    pass


class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    costo: Optional[float] = None
    duracion_minutos: Optional[int] = None
    estado: Optional[bool] = None


class Servicio(ServicioBase):
    Id: int
    fecha_registro: Optional[datetime] = None  # 👈 Permitir None
    fecha_actualizacion: Optional[datetime] = None  # 👈 Permitir None

    class Config:
        from_attributes = True