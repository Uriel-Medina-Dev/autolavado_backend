from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import config.db
import models.model_service as model_service
import schemas.schema_services as schema_service
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
    return db.query(model_service.Servicios).offset(skip).limit(limit).all()


@router.get("/{service_id}")
def read_service(service_id: int, db: Session = Depends(get_db)):
    serv = db.query(model_service.Servicios).filter(model_service.Servicios.Id == service_id).first()
    if not serv:
        raise HTTPException(status_code=404, detail="Service not found")
    return serv


@router.post("/", status_code=201)
def create_service(service: schema_service.ServicioCreate, db: Session = Depends(get_db)):
    db_serv = model_service.Servicios(
        nombre=service.nombre,
        descripcion=service.descripcion,
        costo=service.costo,
        duracion_minutos=service.duaracion_minutos,
        estado=service.estado
    )
    db.add(db_serv)
    db.commit()
    db.refresh(db_serv)
    return db_serv


@router.put("/{service_id}")
def update_service(service_id: int, service: schema_service.ServicioUpdate, db: Session = Depends(get_db)):
    db_serv = db.query(model_service.Servicios).filter(model_service.Servicios.Id == service_id).first()
    if not db_serv:
        raise HTTPException(status_code=404, detail="Service not found")
    for field, value in service.dict(exclude_unset=True).items():
        setattr(db_serv, field if field in db_serv.__dict__ else field, value)
    db.commit()
    db.refresh(db_serv)
    return db_serv


@router.delete("/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    db_serv = db.query(model_service.Servicios).filter(model_service.Servicios.Id == service_id).first()
    if not db_serv:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(db_serv)
    db.commit()
    return {"ok": True}
