from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional
from models.model_vehicles_services import SolicitudEstatus


class UsuariosVehiculoServicioBase(BaseModel):
    vehicle_Id: int
    cajero_Id: int
    operativo_Id: int
    servicio_Id: int
    date: date
    time: time
    estatus: SolicitudEstatus
    estado: bool = True


class UsuariosVehiculoServicioCreate(UsuariosVehiculoServicioBase):
    pass


class UsuariosVehiculoServicioUpdate(BaseModel):
    vehicle_Id: Optional[int] = None
    cajero_Id: Optional[int] = None
    operativo_Id: Optional[int] = None
    servicio_Id: Optional[int] = None
    date: Optional[date] = None
    time: Optional[time] = None
    estatus: Optional[SolicitudEstatus] = None
    estado: Optional[bool] = None


class UsuariosVehiculoServicio(UsuariosVehiculoServicioBase):
    Id: int
    fecha_registro: Optional[datetime] = None  # 👈 Permitir None
    fecha_actualizacion: Optional[datetime] = None  # 👈 Permitir None

    class Config:
        from_attributes = True