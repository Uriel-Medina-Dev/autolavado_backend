"""contendra el crud de usuarios"""
from sqlalchemy.orm import Session
from models.model_user import User
from schemas.schema_user import UsuarioCreate, UsuarioUpdate
from core.security import get_password_hash
from datetime import datetime


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.Id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.user == username).first()


def create_user(db: Session, user: UsuarioCreate):
    """Crear un nuevo usuario - las fechas se asignan automáticamente"""
    db_user = User(
        rol_Id=user.rol_Id,
        user_name=user.user_name,
        user_1lastname=user.user_1lastname,
        user_2lastname=user.user_2lastname,
        user=user.user,
        user_password=get_password_hash(user.user_password),
        user_address=user.user_address,
        user_phone=user.user_phone,
        status=user.status if user.status is not None else True,
        creation_date=datetime.now(),  # Fecha actual
        modification_date=datetime.now()  # Fecha actual
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: UsuarioUpdate):
    db_user = db.query(User).filter(User.Id == user_id).first()
    if db_user:
        update_data = user.dict(exclude_unset=True)
        
        # Si hay contraseña nueva, hashearla
        if "user_password" in update_data and update_data["user_password"]:
            update_data["user_password"] = get_password_hash(update_data["user_password"])
        
        # Actualizar campos
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        # Actualizar fecha de modificación
        db_user.modification_date = datetime.now()
        
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.Id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user