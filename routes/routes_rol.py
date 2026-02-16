from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import config.db, models.model_rol, schemas.schema_rol, crud.crud_rol
from typing import List

rol = APIRouter()

models.model_rol.Base.metadata.create_all(bind=config.db.engine)

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@rol.get("/rol/", response_model=List[schemas.schema_rol.Rol],tags=["Roles"])
async def read_rols(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_rol=crud.crud_rol.get_rol(db=db, skip=skip, limit=limit)
    return db_rol
