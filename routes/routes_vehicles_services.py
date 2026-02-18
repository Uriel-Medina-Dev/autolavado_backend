from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import config.db
import models.model_vehicles_services as model_vs
import schemas.schema_vehicles_services as schema_vs
import crud.crud_vehicles_services as crud
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
    return crud.get_vehicles_services(db=db, skip=skip, limit=limit)


@router.get("/{vs_id}")
def read_vs_item(vs_id: int, db: Session = Depends(get_db)):
    item = crud.get_vehicle_service_by_id(db=db, vs_id=vs_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", status_code=201)
def create_vs(item: schema_vs.UsuariosVehiculoServicioCreate, db: Session = Depends(get_db)):
    return crud.create_vehicle_service(db=db, vs=item)


@router.put("/{vs_id}")
def update_vs(vs_id: int, item: schema_vs.UsuariosVehiculoServicioUpdate, db: Session = Depends(get_db)):
    db_item = crud.update_vehicle_service(db=db, vs_id=vs_id, vs=item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.delete("/{vs_id}", status_code=204)
def delete_vs(vs_id: int, db: Session = Depends(get_db)):
    db_item = crud.delete_vehicle_service(db=db, vs_id=vs_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"ok": True}
