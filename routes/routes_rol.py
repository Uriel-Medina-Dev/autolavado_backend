from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import config.db
import models.model_rols
import schemas.schema_rols
import crud.crud_rols as crud
from typing import List
from routes.routes_auth import get_current_user
import models.model_user as model_user

# router with prefix and default tags
rol = APIRouter(prefix="/rol", tags=["Roles"])

# Crear tablas si no existen
models.model_rols.Base.metadata.create_all(bind=config.db.engine)


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@rol.get("/", response_model=List[schemas.schema_rols.Rol])
async def read_rols(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_rol = crud.get_rol(db=db, skip=skip, limit=limit)
    return db_rol

@rol.get("/{rol_id}", response_model=schemas.schema_rols.Rol)
async def read_rol(rol_id: int,current_user: model_user.User = Depends(get_current_user),db: Session = Depends(get_db)):
    db_rol = crud.get_rol_by_id(db=db, rol_id=rol_id)
    if not db_rol:
        raise HTTPException(status_code=404, detail="Rol not found")
    return db_rol

@rol.post("/", response_model=schemas.schema_rols.Rol)
async def create_rol(rol: schemas.schema_rols.RolCreate,current_user: model_user.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_rol(db=db, rol=rol)

@rol.put("/{rol_id}", response_model=schemas.schema_rols.Rol)
async def update_rol(rol_id: int, rol: schemas.schema_rols.RolUpdate, current_user: model_user.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rol = crud.update_rol(db=db, id=rol_id, rol=rol)
    if not db_rol:
        raise HTTPException(status_code=404, detail="Rol not found")
    return db_rol

@rol.delete("/{rol_id}", status_code=204)
async def delete_rol(rol_id: int, current_user: model_user.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rol = crud.delete_rol(db=db, id=rol_id)
    if not db_rol:
        raise HTTPException(status_code=404, detail="Rol not found")
    # returning 204 no-content, body is ignored
    return None
