'''contendra el crud de roles'''
import models.model_rols
import schemas.schema_rols
from sqlalchemy.orm import Session

def get_rol(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.model_rol.Rol).offset(skip).limit(limit).all()

def get_rol_by_name(db: Session, name:str):
    return db.query(models.model_rols.Rols).filter(models.model_rols.Rols.name == name).first()

def create_rol(db: Session, rol: schemas.schema_rols.RolCreate):
    db_rol = models.model_rols.Rols(
        name = rol.name,
        status = rol.status,
        register_date= rol.creation_date,
        date_update = rol.update_date
    )
    db.add(db_rol)
    db.commit()
    db.refresh(db_rol)
    return db_rol

def update_rol(db:Session, id:int, rol:schemas.schema_rols.RolUpdate):
    db_rol = db.query()