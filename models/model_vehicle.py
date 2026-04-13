"""Esta clase permite generar el modelo para los vehiculos"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.db import Base


class Vehicle(Base):
    """Clase para especificar tabla vehiculos"""
    __tablename__ = "tbb_vehicles"
    
    Id = Column(Integer, primary_key=True, index=True)
    usuario_Id = Column(Integer, ForeignKey("tbb_user.Id"), nullable=False)
    placa = Column(String(15), nullable=False, unique=True)
    modelo = Column(String(30))
    serie = Column(String(60))
    color = Column(String(60))
    tipo = Column(String(250))
    anio = Column(Integer)
    estado = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    usuario = relationship("User", back_populates="vehiculos")
    servicios = relationship("VehiculoServicio", back_populates="vehiculo")