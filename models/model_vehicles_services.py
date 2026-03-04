"""Esta clase permite generar el modelo para las ventas y asignaciones"""
from sqlalchemy import Column, Integer, Boolean, DateTime, Date, Time, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from config.db import Base


class SolicitudEstatus(enum.Enum):
    """Clase para especificar estatus de solicitud"""
    Programada = "Programada"
    Proceso = "Proceso"
    Realizada = "Realizada"
    Cancelada = "Cancelada"


class VehiculoServicio(Base):
    """Clase para especificar tabla de servicios por vehículo"""
    __tablename__ = "tbd_vehicles_services"
    
    Id = Column(Integer, primary_key=True, index=True)
    vehicle_Id = Column(Integer, ForeignKey("tbb_vehicles.Id"), nullable=False)
    cajero_Id = Column(Integer, ForeignKey("tbb_user.Id"), nullable=False)
    operativo_Id = Column(Integer, ForeignKey("tbb_user.Id"), nullable=False)
    servicio_Id = Column(Integer, ForeignKey("tbc_servicios.Id"), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    estatus = Column(SqlEnum(SolicitudEstatus), nullable=False, default=SolicitudEstatus.Programada)
    estado = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    vehiculo = relationship("Vehicle", back_populates="servicios")
    cajero = relationship("User", back_populates="servicios_como_cajero", foreign_keys=[cajero_Id])
    operativo = relationship("User", back_populates="servicios_como_operativo", foreign_keys=[operativo_Id])
    servicio = relationship("Servicios", back_populates="solicitudes")