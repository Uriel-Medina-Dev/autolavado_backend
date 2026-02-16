from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import config.db
import models.model_vehicles_services as model_vs
import schemas.schema_vehicles_services as schema_vs
from typing import List

router = APIRouter(prefix="/vehicle_services", tags=["VehicleServices"])


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schema_vs.UsuariosVehiculoServicio])
def read_vs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(model_vs.VehiculoServicio).offset(skip).limit(limit).all()


@router.get("/{vs_id}")
def read_vs_item(vs_id: int, db: Session = Depends(get_db)):
    item = db.query(model_vs.VehiculoServicio).filter(model_vs.VehiculoServicio.Id == vs_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", status_code=201)
def create_vs(item: schema_vs.UsuariosVehiculoServicioCreate, db: Session = Depends(get_db)):
    db_item = model_vs.VehiculoServicio(
        vehicle_Id=getattr(item, 'vehicle_Id', None),
        cajero_Id=getattr(item, 'cajero_Id', None),
        operativo_Id=getattr(item, 'operativo_Id', None),
        servicio_Id=getattr(item, 'servicio_Id', None),
        date=getattr(item, 'fecha', None),
        time=getattr(item, 'hora', None),
        estatus=getattr(item, 'estatus', None),
        estado=getattr(item, 'estado', True)
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/{vs_id}")
def update_vs(vs_id: int, item: schema_vs.UsuariosVehiculoServicioUpdate, db: Session = Depends(get_db)):
    db_item = db.query(model_vs.VehiculoServicio).filter(model_vs.VehiculoServicio.Id == vs_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field if field in db_item.__dict__ else field, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{vs_id}", status_code=204)
def delete_vs(vs_id: int, db: Session = Depends(get_db)):
    db_item = db.query(model_vs.VehiculoServicio).filter(model_vs.VehiculoServicio.Id == vs_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}
