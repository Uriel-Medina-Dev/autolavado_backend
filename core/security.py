from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv

import os
from types import SimpleNamespace

# Cargar las variables de entorno (si existe .env)
load_dotenv()

# Obtener SECRET_KEY desde el .env, usar valor por defecto en desarrollo
SECRET_KEY = os.getenv("SECRET_KEY") or "dev_secret_key_change_me"

# Crear contexto de bcrypt para el cifrado de contraseñas (más compatible que argon2 si no está instalado)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Compatibilidad: mantener alias antiguo si se usa otro nombre
hash_password = get_password_hash

# Configuración de JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tiempo de expiración del token (en minutos)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    """Decodifica un JWT y devuelve un objeto con el campo `user_id` (sub).

    Retorna None si el token es inválido o expirado.
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # El payload suele contener 'sub' con el id de usuario
        user_id = decoded.get("sub") or decoded.get("user_id")
        return SimpleNamespace(user_id=user_id, payload=decoded)
    except JWTError:
        return None


# Mantener compatibilidad con nombre antiguo
verify_token = decode_token