'''Esta clase permite generar el modelo para las ventas y asignaciones'''
from sqlalchemy import Column, Integer, Boolean, DateTime,Date,Time, ForeignKey
from enum import Enum
# pylint: disable=import-error
from config.db import Base

class Solicitud():
    '''Clase para especificar estatus de solicitud'''
    Programada = "Programada"
    Proceso = "Proceso"
    Realizada = "Realizada"
    Cancelada = "Cancelada"

# pylint: disable=too-few-public-methods
class VehiculoServicio(Base):
    '''Clase para especificar tabla vehiculos'''
    __tablemname__ = "tbd_usuario_vehiculo_servicio"
    Id = Column(Integer, primary_key=True, index=True)
    vehiculo_Id = Column(Integer, ForeignKey("tbb_vehiculos.Id"))
    cajero_Id = Column(Integer, ForeignKey("tbb_usuarios.Id"))
    operativo_Id = Column(Integer, ForeignKey("tbb_usarios.Id"))
    servicio_Id = Column(Integer, ForeignKey("tbc_servicios.Id"))
    fecha = Column(Date)
    hora = Column(Time)
    estatus = Column(Enum(Solicitud))
    estado = Column(Boolean)
    fecha_registro = Column(DateTime)
    fecha_actualizacion = Column(DateTime)
