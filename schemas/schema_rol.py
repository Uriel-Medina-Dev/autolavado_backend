'''
Docstring for schemas.schema_rol
'''
from pydantic import BaseModel
from datetime import datetime
class RolBase(BaseModel):
    '''Clase para modelar los campos de tabla Rol'''
    nombre_rol: str
    estado: bool
    fecha_registro: datetime
    fecha_actualizacion: datetime
# pylint: disable=too-few-public-methods, unnecessary-pass
class RolCreate(RolBase):
    '''Clase para crear un Rol basado en la tabla Rols'''
    pass
class RolUpdate(RolBase):
    '''Clase para actualizar un Rol basado en la tabla Rols'''
    pass

class Rol(RolBase):
    '''Clase para realizar operaciones por ID en tabla Rol'''
    Id: int
    class Config:
        '''Utilizar el orm para ejecutar las funcionalidades'''
        orm_mode =True
