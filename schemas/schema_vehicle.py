from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VehiculoBase(BaseModel):
    usuario_Id: int
    placa: str
    modelo: Optional[str] = None
    serie: Optional[str] = None
    color: Optional[str] = None
    tipo: Optional[str] = None
    anio: Optional[int] = None
    estado: bool = True


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoUpdate(BaseModel):
    usuario_Id: Optional[int] = None
    placa: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    color: Optional[str] = None
    tipo: Optional[str] = None
    anio: Optional[int] = None
    estado: Optional[bool] = None


class Vehiculo(VehiculoBase):
    Id: int
    fecha_registro: Optional[datetime] = None  # 👈 Permitir None
    fecha_actualizacion: Optional[datetime] = None  # 👈 Permitir None

    class Config:
        from_attributes = True