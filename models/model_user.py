""" Esta clase representa la tabla de usuarios """
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.db import Base


class User(Base):
    """ En este apartado se define la clase con sus atributos """
    __tablename__ = "tbb_user"
    
    Id = Column(Integer, primary_key=True, index=True)
    rol_Id = Column(Integer, ForeignKey("tbc_rols.id"), nullable=False)
    user_name = Column(String(60), nullable=False)
    user_1lastname = Column(String(60), nullable=False)
    user_2lastname = Column(String(60))
    user = Column(String(60), unique=True, nullable=False)
    user_password = Column(String(255), nullable=False)  # Aumentado a 255 para hash
    user_address = Column(String(160))
    user_phone = Column(String(15))
    status = Column(Boolean, default=True)
    creation_date = Column(DateTime, server_default=func.now(), nullable=False)
    modification_date = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    rol = relationship("Rols", back_populates="usuarios")
    vehiculos = relationship("Vehicle", back_populates="usuario")
    servicios_como_cajero = relationship("VehiculoServicio", back_populates="cajero", foreign_keys="VehiculoServicio.cajero_Id")
    servicios_como_operativo = relationship("VehiculoServicio", back_populates="operativo", foreign_keys="VehiculoServicio.operativo_Id")