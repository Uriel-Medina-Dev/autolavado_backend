'''contendra el crud de roles'''
import models.model_rols
import schemas.schema_rols
from sqlalchemy.orm import Session

def get_rol(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.model_rols.Rols).offset(skip).limit(limit).all()

def get_rol_by_id(db: Session, rol_id: int):
    return db.query(models.model_rols.Rols).filter(models.model_rols.Rols.id == rol_id).first()

def create_rol(db: Session, rol: schemas.schema_rols.RolCreate):
    db_rol = models.model_rols.Rols(
        name=rol.name,
        status=rol.status,
        creation_date=rol.creation_date,
        update_date=rol.update_date
    )
    db.add(db_rol)
    db.commit()
    db.refresh(db_rol)
    return db_rol

def update_rol(db: Session, id: int, rol: schemas.schema_rols.RolUpdate):
    db_rol = db.query(models.model_rols.Rols).filter(models.model_rols.Rols.id == id).first()
    if db_rol:
        for field, value in rol.dict(exclude_unset=True).items():
            setattr(db_rol, field, value)
        db.commit()
        db.refresh(db_rol)
    return db_rol

def delete_rol(db: Session, id: int):
    db_rol = db.query(models.model_rols.Rols).filter(models.model_rols.Rols.id == id).first()
    if db_rol:
        db.delete(db_rol)
        db.commit()
    return db_rol