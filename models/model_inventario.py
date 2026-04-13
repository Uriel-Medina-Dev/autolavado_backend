"""Esta clase representa la tabla de movimientos de inventario"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SqlEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from config.db import Base


class TipoMovimiento(enum.Enum):
    """Tipos de movimiento de inventario"""
    ENTRADA = "Entrada"
    SALIDA = "Salida"
    AJUSTE = "Ajuste"
    DEVOLUCION = "Devolución"
    COMPRA = "Compra"
    VENTA = "Venta"


class Inventario(Base):
    """Modelo para movimientos de inventario"""
    
    __tablename__ = "tbd_inventario"
    
    Id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("tbc_productos.Id"), nullable=False)
    tipo_movimiento = Column(SqlEnum(TipoMovimiento), nullable=False)
    cantidad = Column(Integer, nullable=False)
    stock_anterior = Column(Integer, nullable=False)
    stock_nuevo = Column(Integer, nullable=False)
    
    # Campos de seguimiento
    concepto = Column(String(200), nullable=True)  # Razón del movimiento
    referencia = Column(String(100), nullable=True)  # Número de factura, orden, etc.
    notas = Column(Text, nullable=True)
    
    # Relación con usuario que realizó el movimiento
    usuario_id = Column(Integer, ForeignKey("tbb_user.Id"), nullable=False)
    
    # Campos de auditoría
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    estado = Column(Boolean, default=True)
    
    # Relaciones
    producto = relationship("Producto", back_populates="movimientos_inventario")
    usuario = relationship("User", back_populates="movimientos_inventario")
    
    def __repr__(self):
        return f"<Inventario(id={self.Id}, producto={self.producto_id}, tipo={self.tipo_movimiento}, cantidad={self.cantidad})>"