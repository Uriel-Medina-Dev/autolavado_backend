from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import config.db
import models.model_user as model_user
import schemas.schema_user as schema_user
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schema_user.Usuario])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(model_user.User).offset(skip).limit(limit).all()


@router.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(model_user.User).filter(model_user.User.Id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", status_code=201)
def create_user(user: schema_user.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = model_user.User(
        user_name=user.nombre,
        user_1lastname=user.primer_apellido,
        user_2lastname=user.segundo_apellido,
        user_address=user.direccion,
        user=user.correo_electronico,
        user_password=user.contrasena,
        user_phone=user.numero_telefono,
        status=user.estado
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/{user_id}")
def update_user(user_id: int, user: schema_user.UsuarioUpdate, db: Session = Depends(get_db)):
    db_user = db.query(model_user.User).filter(model_user.User.Id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in user.dict(exclude_unset=True).items():
        setattr(db_user, field if field in db_user.__dict__ else field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(model_user.User).filter(model_user.User.Id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"ok": True}
