"""CRUD para autenticación"""
from sqlalchemy.orm import Session
from models.model_user import User
from core.security import verify_password, get_password_hash


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Autentica un usuario verificando usuario y contraseña
    
    Args:
        db: Sesión de base de datos
        username: Nombre de usuario
        password: Contraseña en texto plano
        
    Returns:
        User si la autenticación es exitosa, None en caso contrario
    """
    user = db.query(User).filter(User.user == username).first()
    if not user:
        return None
    if not verify_password(password, user.user_password):
        return None
    return user


def hash_password_for_user(db: Session, user_id: int, new_password: str) -> bool:
    """
    Actualiza la contraseña de un usuario con hash
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        new_password: Nueva contraseña en texto plano
        
    Returns:
        True si se actualizó correctamente
    """
    user = db.query(User).filter(User.Id == user_id).first()
    if not user:
        return False
    user.user_password = get_password_hash(new_password)
    db.commit()
    return True
