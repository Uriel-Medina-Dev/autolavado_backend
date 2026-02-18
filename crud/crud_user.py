'''contendra el crud de usuarios'''
import models.model_user
import schemas.schema_user
from sqlalchemy.orm import Session
from core.security import get_password_hash

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.model_user.User).offset(skip).limit(limit).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.model_user.User).filter(models.model_user.User.Id == user_id).first()

def create_user(db: Session, user: schemas.schema_user.UsuarioCreate):
    db_user = models.model_user.User(
        rol_Id=user.rol_Id,
        user_name=user.user_name,
        user_1lastname=user.user_1lastname,
        user_2lastname=user.user_2lastname,
        user=user.user,
        user_password=get_password_hash(user.user_password),
        user_address=user.user_address,
        user_phone=user.user_phone,
        status=user.status,
        creation_date=user.creation_date,
        modification_date=user.modification_date
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.schema_user.UsuarioUpdate):
    db_user = db.query(models.model_user.User).filter(models.model_user.User.Id == user_id).first()
    if db_user:
        for field, value in user.dict(exclude_unset=True).items():
            if field == "user_password" and value:
                value = get_password_hash(value)
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.model_user.User).filter(models.model_user.User.Id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user