''' Esta clase representa la tabla de usuarios '''
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class User(Base):
    ''' En este apartado se define la clase con sus atributos '''
    __tablename__ = "tbb_user"
    
    Id = Column(Integer, primary_key = True, index = True)
    rol_Id = Column(Integer, ForeignKey("tbc_rols.id"))
    user_name = Column (String(60))
    user_1lastname = Column (String(60))
    user_2lastname = Column (String(60))
    user = Column(String(60))
    user_password = Column(String(60))
    user_address = Column(String(160))
    user_phone = Column(String(15))
    status = Column(Boolean)
    creation_date = Column(DateTime)
    modification_date = Column(DateTime)
    
    # Relaciones
    rol = relationship("Rols", back_populates="usuarios")
    vehiculos = relationship("Vehicle", back_populates="usuario", foreign_keys="Vehicle.usuario_Id")
    servicios_como_cajero = relationship("VehiculoServicio", back_populates="cajero", foreign_keys="VehiculoServicio.cajero_Id")
    servicios_como_operativo = relationship("VehiculoServicio", back_populates="operativo", foreign_keys="VehiculoServicio.operativo_Id")
