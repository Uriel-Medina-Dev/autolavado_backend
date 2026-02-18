'''
Docstring for schemas.schema_usuario
'''
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class UsuarioBase(BaseModel):
    '''Clase para modelar los campos de tabla Usuarios'''
    rol_Id: int
    user_name: str
    user_1lastname: str
    user_2lastname: str
    user: str
    user_password: str
    user_address: str
    user_phone: str
    status: bool
    creation_date: datetime
    modification_date: datetime
# pylint: disable=too-few-public-methods, unnecessary-pass
class UsuarioCreate(UsuarioBase):
    '''Clase para crear un Usuario basado en la tabla Usuario'''
    pass
class UsuarioUpdate(UsuarioBase):
    '''Clase para actualizar un Usuario basado en la tabla Usuario'''
    pass

class Usuario(UsuarioBase):
    '''Clase para realizar operaciones por ID en tabla Usuario'''
    Id: int
    class Config:
        '''Utilizar el orm para ejecutar las funcionalidades'''
        orm_mode = True

class UsuarioLogin(BaseModel):
    '''Clase para realizar login por numero de telefono o correo'''
    user: Optional[str] = None
    user_phone: Optional[str] = None
    user_password: str
