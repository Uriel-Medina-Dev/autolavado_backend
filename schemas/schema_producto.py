from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class ProductoBase(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=50)
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=50)
    precio_compra: float = Field(..., gt=0)
    precio_venta: float = Field(..., gt=0)
    stock_actual: int = Field(0, ge=0)
    stock_minimo: int = Field(5, ge=0)
    unidad_medida: Optional[str] = Field(None, max_length=20)
    proveedor: Optional[str] = Field(None, max_length=100)
    ubicacion: Optional[str] = Field(None, max_length=50)
    estado: bool = True
    usuario_registro_id: Optional[int] = None
    
    @validator('precio_venta')
    def precio_venta_mayor_que_compra(cls, v, values):
        if 'precio_compra' in values and v < values['precio_compra']:
            raise ValueError('El precio de venta debe ser mayor o igual al precio de compra')
        return v


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, min_length=3, max_length=50)
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=50)
    precio_compra: Optional[float] = Field(None, gt=0)
    precio_venta: Optional[float] = Field(None, gt=0)
    stock_actual: Optional[int] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    unidad_medida: Optional[str] = Field(None, max_length=20)
    proveedor: Optional[str] = Field(None, max_length=100)
    ubicacion: Optional[str] = Field(None, max_length=50)
    estado: Optional[bool] = None
    usuario_registro_id: Optional[int] = None


class Producto(ProductoBase):
    Id: int
    fecha_registro: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    
    # Información adicional (opcional)
    usuario_registro_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True