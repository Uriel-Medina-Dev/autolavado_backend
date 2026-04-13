"""Esquemas para autenticación"""
from pydantic import BaseModel


class Login(BaseModel):
    """Esquema para el login"""
    user: str
    password: str


class Token(BaseModel):
    """Esquema para la respuesta del token"""
    access_token: str
    token_type: str
    user_id: int
