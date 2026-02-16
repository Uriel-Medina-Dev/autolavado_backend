'''Esta clase permite generar el modelo para los servicios'''
from sqlalchemy import Column, Integer, String, Boolean,Float,DateTime
# pylint: disable=import-error
from config.db import Base

# pylint: disable=too-few-public-methods
class Servicios(Base):
    '''Clase para especificar tabla de servicios'''
    __tablename__ = "tbc_servicios"
    Id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(60))
    descripcion = Column(String(150))
    costo = Column(Float)
    duracion_minutos = Column(Integer)
    estado = Column(Boolean)
    fecha_registro = Column(DateTime)
    fecha_actualizacion = Column(DateTime)
