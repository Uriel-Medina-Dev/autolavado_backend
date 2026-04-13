from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from models.model_inventario import TipoMovimiento


class InventarioBase(BaseModel):
    producto_id: int
    tipo_movimiento: TipoMovimiento
    cantidad: int = Field(..., gt=0)
    concepto: Optional[str] = Field(None, max_length=200)
    referencia: Optional[str] = Field(None, max_length=100)
    notas: Optional[str] = None
    usuario_id: int
    estado: bool = True


class InventarioCreate(InventarioBase):
    pass


class InventarioUpdate(BaseModel):
    concepto: Optional[str] = Field(None, max_length=200)
    referencia: Optional[str] = Field(None, max_length=100)
    notas: Optional[str] = None
    estado: Optional[bool] = None


class Inventario(InventarioBase):
    Id: int
    stock_anterior: int
    stock_nuevo: int
    fecha_registro: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    
    # Información adicional (opcional)
    producto_nombre: Optional[str] = None
    producto_codigo: Optional[str] = None
    usuario_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True


class MovimientoStock(BaseModel):
    """Schema para realizar un movimiento de stock"""
    producto_id: int
    tipo_movimiento: TipoMovimiento
    cantidad: int = Field(..., gt=0)
    concepto: Optional[str] = Field(None, max_length=200)
    referencia: Optional[str] = Field(None, max_length=100)
    notas: Optional[str] = None


class ResumenInventario(BaseModel):
    """Resumen de inventario por producto"""
    producto_id: int
    producto_nombre: str
    producto_codigo: str
    stock_actual: int
    stock_minimo: int
    total_entradas: int
    total_salidas: int
    ultimo_movimiento: Optional[datetime] = None
    estado: str  # "Normal", "Bajo stock", "Sin stock"