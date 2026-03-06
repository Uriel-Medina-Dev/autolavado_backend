from datetime import datetime, timedelta
from jose import JWTError, jwt
from jose.exceptions import JWTClaimsError, ExpiredSignatureError
from dotenv import load_dotenv
import bcrypt
import os

# Cargar las variables de entorno
load_dotenv()

# Obtener SECRET_KEY desde el .env
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("⚠️ ADVERTENCIA: SECRET_KEY no está definida en .env, usando valor por defecto para desarrollo")
    SECRET_KEY = "dev_secret_key"

# Configuración de JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas por defecto

def get_password_hash(password: str) -> str:
    """Genera un hash de la contraseña usando bcrypt"""
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash"""
    if isinstance(plain_password, str):
        plain_bytes = plain_password.encode('utf-8')
    else:
        plain_bytes = plain_password
        
    if isinstance(hashed_password, str):
        hashed_bytes = hashed_password.encode('utf-8')
    else:
        hashed_bytes = hashed_password
    
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

# Mantener compatibilidad
hash_password = get_password_hash

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Crea un token JWT - Asegura que el subject sea string"""
    to_encode = data.copy()
    
    # IMPORTANTE: Convertir el subject a string si no lo es
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    print(f"🔐 Creando token para user_id: {to_encode.get('sub')} (tipo: {type(to_encode.get('sub'))})")
    print(f"🔐 Expira: {expire}")
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """Decodifica un JWT y devuelve un objeto con el campo user_id"""
    try:
        print(f"🔓 Decodificando token: {token[:30]}...")
        
        # Decodificar el token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        print(f"✅ Token decodificado exitosamente")
        print(f"📦 Payload: {decoded}")
        
        # El payload contiene 'sub' con el id de usuario (ahora como string)
        user_id = decoded.get("sub")
        
        if not user_id:
            print("❌ No se encontró 'sub' en el payload")
            return None
        
        # Convertir a entero si es necesario (para la BD)
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            user_id_int = user_id
        
        # Verificar expiración
        if "exp" in decoded:
            exp_date = datetime.fromtimestamp(decoded["exp"])
            now = datetime.utcnow()
            print(f"📅 Token expira: {exp_date}")
            print(f"📅 Ahora: {now}")
            
            if exp_date < now:
                print("❌ Token EXPIRADO!")
                return None
            else:
                time_left = exp_date - now
                print(f"⏳ Tiempo restante: {time_left}")
        
        # Crear un objeto simple para mantener compatibilidad
        from types import SimpleNamespace
        return SimpleNamespace(user_id=user_id_int, payload=decoded)
        
    except ExpiredSignatureError:
        print("❌ Token expirado (ExpiredSignatureError)")
        return None
    except JWTClaimsError as e:
        print(f"❌ Error de claims JWT: {e}")
        return None
    except JWTError as e:
        print(f"❌ Error JWT: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado decodificando token: {e}")
        return None

# Mantener compatibilidad
verify_token = decode_token