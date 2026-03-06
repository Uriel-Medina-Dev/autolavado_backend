from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional


class CajeroBase(BaseModel):
    usuario_id: int
    numero_empleado: str = Field(..., min_length=3, max_length=20)
    turno: str = Field(..., pattern="^(Matutino|Vespertino|Nocturno)$")  # 👈 CORREGIDO
    numero_caja: Optional[int] = Field(None, ge=1)
    fecha_contratacion: date
    salario: Optional[float] = Field(None, gt=0)
    contacto_emergencia_nombre: Optional[str] = Field(None, max_length=100)
    contacto_emergencia_telefono: Optional[str] = Field(None, max_length=15)
    contacto_emergencia_parentesco: Optional[str] = Field(None, max_length=30)
    banco: Optional[str] = Field(None, max_length=50)
    cuenta_bancaria: Optional[str] = Field(None, max_length=30)
    clabe: Optional[str] = Field(None, max_length=20)
    estado: bool = True


class CajeroCreate(CajeroBase):
    pass


class CajeroUpdate(BaseModel):
    turno: Optional[str] = Field(None, pattern="^(Matutino|Vespertino|Nocturno)$")  # 👈 CORREGIDO
    numero_caja: Optional[int] = Field(None, ge=1)
    salario: Optional[float] = Field(None, gt=0)
    contacto_emergencia_nombre: Optional[str] = Field(None, max_length=100)
    contacto_emergencia_telefono: Optional[str] = Field(None, max_length=15)
    contacto_emergencia_parentesco: Optional[str] = Field(None, max_length=30)
    banco: Optional[str] = Field(None, max_length=50)
    cuenta_bancaria: Optional[str] = Field(None, max_length=30)
    clabe: Optional[str] = Field(None, max_length=20)
    estado: Optional[bool] = None


class Cajero(CajeroBase):
    Id: int
    fecha_registro: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    
    # Información adicional del usuario (opcional)
    usuario_nombre_completo: Optional[str] = None
    usuario_user: Optional[str] = None
    usuario_telefono: Optional[str] = None
    
    class Config:
        from_attributes = True


class CajeroConUsuario(Cajero):
    """Versión extendida que incluye todos los datos del usuario"""
    usuario_info: Optional[dict] = None
    
    class Config:
        from_attributes = True


class CambioTurno(BaseModel):
    """Schema para cambiar turno de cajero"""
    turno: str = Field(..., pattern="^(Matutino|Vespertino|Nocturno)$")  # 👈 CORREGIDO
    motivo: Optional[str] = Field(None, max_length=200)


class AsignarCaja(BaseModel):
    """Schema para asignar/desasignar caja"""
    numero_caja: Optional[int] = Field(None, ge=1)
    motivo: Optional[str] = Field(None, max_length=200)  