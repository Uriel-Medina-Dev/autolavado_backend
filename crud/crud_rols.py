"""contendra el crud de roles"""
from sqlalchemy.orm import Session
from models.model_rols import Rols
from schemas.schema_rols import RolCreate, RolUpdate
from datetime import datetime


def get_rol(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Rols).offset(skip).limit(limit).all()


def get_rol_by_id(db: Session, rol_id: int):
    return db.query(Rols).filter(Rols.id == rol_id).first()


def create_rol(db: Session, rol: RolCreate):
    """Crear un nuevo rol - las fechas se asignan automáticamente"""
    db_rol = Rols(
        name=rol.name,
        status=rol.status,
        creation_date=datetime.now(),  # Fecha actual
        update_date=datetime.now()  # Fecha actual
    )
    db.add(db_rol)
    db.commit()
    db.refresh(db_rol)
    return db_rol


def update_rol(db: Session, id: int, rol: RolUpdate):
    db_rol = db.query(Rols).filter(Rols.id == id).first()
    if db_rol:
        update_data = rol.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rol, field, value)
        
        # Actualizar fecha de modificación
        db_rol.update_date = datetime.now()
        
        db.commit()
        db.refresh(db_rol)
    return db_rol


def delete_rol(db: Session, id: int):
    db_rol = db.query(Rols).filter(Rols.id == id).first()
    if db_rol:
        db.delete(db_rol)
        db.commit()
    return db_rol