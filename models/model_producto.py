"""Esta clase representa la tabla de productos"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.db import Base


class Producto(Base):
    """Modelo para productos del autolavado"""
    
    __tablename__ = "tbc_productos"
    
    Id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=True)
    precio_compra = Column(Float, nullable=False, default=0)
    precio_venta = Column(Float, nullable=False, default=0)
    stock_actual = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=5)
    unidad_medida = Column(String(20), nullable=True)
    proveedor = Column(String(100), nullable=True)
    ubicacion = Column(String(50), nullable=True)
    estado = Column(Boolean, default=True)
    
    # Relación con usuario que registró
    usuario_registro_id = Column(Integer, ForeignKey("tbb_user.Id"), nullable=True)
    usuario_registro = relationship("User", back_populates="productos_registrados")
    
    # Campos de auditoría
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<Producto(id={self.Id}, nombre='{self.nombre}')>"