'''contendra el crud de roles'''
import models.model_rol
import schemas.schema_rol
from sqlalchemy.orm import Session

def get_rol(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.model_rol.Rol).offset(skip).limit(limit).all()