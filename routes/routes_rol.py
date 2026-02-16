from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import config.db
import models.model_rols
import schemas.schema_rols
import crud.crud_rols as crud
from typing import List


rol = APIRouter()

# Crear tablas si no existen
models.model_rols.Base.metadata.create_all(bind=config.db.engine)


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@rol.get("/rol/", response_model=List[schemas.schema_rols.Rol], tags=["Roles"])
async def read_rols(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_rol = crud.get_rol(db=db, skip=skip, limit=limit)
    return db_rol
