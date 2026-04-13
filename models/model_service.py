"""Esta clase permite generar el modelo para los servicios"""
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.db import Base


class Servicios(Base):
    """Clase para especificar tabla de servicios"""
    __tablename__ = "tbc_servicios"
    
    Id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(60), nullable=False)
    descripcion = Column(String(150))
    costo = Column(Float, nullable=False, default=0.0)
    duracion_minutos = Column(Integer, nullable=False, default=30)
    estado = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    solicitudes = relationship("VehiculoServicio", back_populates="servicio")