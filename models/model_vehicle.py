'''Esta clase permite generar el modelo para los vehiculos'''
from sqlalchemy import Column, Integer, String, Boolean, DateTime,ForeignKey
from sqlalchemy.sql import func
# pylint: disable=import-error
from config.db import Base

# pylint: disable=too-few-public-methods
class Vehicle(Base):
    '''Clase para especificar tabla vehiculos'''
    __tablename__ = "tbb_vehicles"
    Id = Column(Integer, primary_key=True, index=True)
    usuario_Id = Column(Integer, ForeignKey("tbb_user.Id"))
    placa = Column(String(15))
    modelo = Column(String(30))
    serie = Column(String(60))
    color = Column(String(60))
    tipo = Column(String(250))
    anio = Column(Integer)
    estado = Column(Boolean)
    fecha_registro = Column(DateTime)
    fecha_actualizacion = Column(DateTime)