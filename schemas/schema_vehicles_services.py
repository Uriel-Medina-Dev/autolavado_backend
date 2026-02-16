'''
Docstring for schemas.schema_usuario_vehiculo_servicio
'''
from datetime import datetime,date,time
from pydantic import BaseModel

class UsuariosVehiculoServicioBase(BaseModel):
    '''Clase para modelar los campos de tabla Usuarios_Vehiculo_Servicio'''
    fecha: date
    hora: date
    estatus: str
    estado: bool
    fecha_registro: datetime
    fecha_actualizacion: datetime
# pylint: disable=too-few-public-methods, unnecessary-pass
class UsuariosVehiculoServicioCreate(UsuariosVehiculoServicioBase):
    '''Clase para asignar un servicio a un vehioculo'''
    pass
class UsuariosVehiculoServicioUpdate(UsuariosVehiculoServicioBase):
    '''Clase para actualizar un servicio a un vehiculo'''
    pass

class UsuariosVehiculoServicio(UsuariosVehiculoServicioBase):
    '''Clase para realizar operaciones por ID en tabla '''
    Id: int
    class Config:
        '''Utilizar el orm para ejecutar las funcionalidades'''
        orm_mode =True
