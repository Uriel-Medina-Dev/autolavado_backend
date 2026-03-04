from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import bcrypt
import os
from types import SimpleNamespace

# Cargar las variables de entorno
load_dotenv()

# Obtener SECRET_KEY desde el .env
SECRET_KEY = os.getenv("SECRET_KEY") or "dev_secret_key_change_me"

# Configuración de JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_password_hash(password: str) -> str:
    """Genera un hash de la contraseña usando bcrypt"""
    # Convertir a bytes si es string
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    
    # Generar salt y hash
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Devolver como string
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash"""
    # Convertir a bytes
    if isinstance(plain_password, str):
        plain_bytes = plain_password.encode('utf-8')
    else:
        plain_bytes = plain_password
        
    if isinstance(hashed_password, str):
        hashed_bytes = hashed_password.encode('utf-8')
    else:
        hashed_bytes = hashed_password
    
    # Verificar
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

# Mantener compatibilidad (corregido el typo)
hash_password = get_password_hash

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """Decodifica un JWT y devuelve un objeto con el campo user_id"""
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # El payload contiene 'sub' con el id de usuario
        user_id = decoded.get("sub")
        return SimpleNamespace(user_id=user_id, payload=decoded)
    except JWTError:
        return None

# Mantener compatibilidad
verify_token = decode_token