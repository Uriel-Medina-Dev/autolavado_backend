from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import config.db
import models.model_service as model_service
import schemas.schema_services as schema_service
import crud.crud_service as crud
from typing import List

router = APIRouter(prefix="/services", tags=["Services"])


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schema_service.Servicio])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_services(db=db, skip=skip, limit=limit)


@router.get("/{service_id}")
def read_service(service_id: int, db: Session = Depends(get_db)):
    serv = crud.get_service_by_id(db=db, service_id=service_id)
    if not serv:
        raise HTTPException(status_code=404, detail="Service not found")
    return serv


@router.post("/", status_code=201)
def create_service(service: schema_service.ServicioCreate, db: Session = Depends(get_db)):
    return crud.create_service(db=db, service=service)


@router.put("/{service_id}")
def update_service(service_id: int, service: schema_service.ServicioUpdate, db: Session = Depends(get_db)):
    db_serv = crud.update_service(db=db, service_id=service_id, service=service)
    if not db_serv:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_serv


@router.delete("/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    db_serv = crud.delete_service(db=db, service_id=service_id)
    if not db_serv:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"ok": True}
