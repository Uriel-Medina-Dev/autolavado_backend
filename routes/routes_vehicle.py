from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import config.db
import models.model_vehicle as model_vehicle
import schemas.schema_vehicle as schema_vehicle
from typing import List

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schema_vehicle.Vehiculo])
def read_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(model_vehicle.Vehicle).offset(skip).limit(limit).all()


@router.get("/{vehicle_id}")
def read_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    veh = db.query(model_vehicle.Vehicle).filter(model_vehicle.Vehicle.Id == vehicle_id).first()
    if not veh:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return veh


@router.post("/", status_code=201)
def create_vehicle(vehicle: schema_vehicle.VehiculoCreate, db: Session = Depends(get_db)):
    db_veh = model_vehicle.Vehicle(
        placa=vehicle.placa,
        modelo=vehicle.modelo,
        serie=vehicle.serie,
        color=vehicle.color,
        tipo=vehicle.tipo,
        anio=vehicle.anio,
        estado=vehicle.estado
    )
    db.add(db_veh)
    db.commit()
    db.refresh(db_veh)
    return db_veh


@router.put("/{vehicle_id}")
def update_vehicle(vehicle_id: int, vehicle: schema_vehicle.VehiculoUpdate, db: Session = Depends(get_db)):
    db_veh = db.query(model_vehicle.Vehicle).filter(model_vehicle.Vehicle.Id == vehicle_id).first()
    if not db_veh:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for field, value in vehicle.dict(exclude_unset=True).items():
        setattr(db_veh, field if field in db_veh.__dict__ else field, value)
    db.commit()
    db.refresh(db_veh)
    return db_veh


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    db_veh = db.query(model_vehicle.Vehicle).filter(model_vehicle.Vehicle.Id == vehicle_id).first()
    if not db_veh:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(db_veh)
    db.commit()
    return {"ok": True}
