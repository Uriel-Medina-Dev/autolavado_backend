"""Rutas de autenticación"""
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import config.db
from schemas.schema_auth import Login, Token
from core.security import create_access_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from crud.crud_auth import authenticate_user
from models.model_user import User

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """
    Valida el token JWT y retorna el usuario actual
    """
    token = credentials.credentials
    
    # Debug
    print(f"🔍 Token recibido en get_current_user: {token[:30]}...")
    
    token_data = decode_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"🔍 Buscando usuario con ID: {token_data.user_id}")
    
    # Buscar por Id (con mayúscula) en la tabla tbb_user
    user = db.query(User).filter(User.Id == token_data.user_id).first()
    
    if user is None:
        print(f"❌ Usuario con ID {token_data.user_id} no encontrado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"✅ Usuario autenticado: {user.user}")
    return user


@router.post("/login", response_model=Token)
async def login(credentials: Login, db: Session = Depends(get_db)):
    """
    Endpoint de login que genera un JWT token
    """
    user = authenticate_user(db, credentials.user, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.Id}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.Id
    }


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Obtiene la información del usuario actual autenticado
    """
    return {
        "id": current_user.Id,
        "username": current_user.user,
        "name": current_user.user_name,
        "lastname": f"{current_user.user_1lastname} {current_user.user_2lastname or ''}",
        "email": current_user.user,
        "rol_id": current_user.rol_Id
    }