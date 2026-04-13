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
    descuento: Optional[float] = 0  # 👈 NUEVO
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
    descuento: Optional[float] = None  # 👈 NUEVO
    estado: Optional[bool] = None


class UsuariosVehiculoServicio(UsuariosVehiculoServicioBase):
    Id: int
    fecha_registro: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# 👇 NUEVO SCHEMA PARA RESPUESTA COMPLETA CON JOIN
class AsignacionCompleta(BaseModel):
    """Schema para respuesta con toda la información de la asignación"""
    # Información de la asignación
    asignacion_id: int
    fecha: date
    hora: time
    estatus: str
    descuento: float
    fecha_registro: Optional[datetime] = None
    
    # Información del vehículo
    vehiculo_id: int
    placa: str
    vehiculo_modelo: Optional[str] = None
    vehiculo_color: Optional[str] = None
    vehiculo_tipo: Optional[str] = None
    vehiculo_anio: Optional[int] = None
    
    # Información del propietario
    propietario_id: int
    propietario_nombre: str
    propietario_apellidos: str
    propietario_telefono: Optional[str] = None
    
    # Información del cajero que atendió
    cajero_id: int
    cajero_nombre: str
    cajero_apellidos: str
    
    # Información del operativo que realizó el servicio
    operativo_id: int
    operativo_nombre: str
    operativo_apellidos: str
    
    # Información del servicio
    servicio_id: int
    servicio_nombre: str
    servicio_descripcion: Optional[str] = None
    servicio_precio_original: float
    
    # Cálculos
    precio_final: float  # Precio después del descuento
    
    class Config:
        from_attributes = True


# 👇 NUEVO SCHEMA PARA RESUMEN DE VENTAS
class ResumenVentas(BaseModel):
    total_asignaciones: int
    total_ingresos: float
    total_descuentos: float
    promedio_por_servicio: float
    servicio_mas_solicitado: Optional[str] = None
    cajero_destacado: Optional[str] = None
    periodo: str