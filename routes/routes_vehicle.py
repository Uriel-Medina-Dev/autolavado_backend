from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import config.db
import models.model_vehicle as model_vehicle
import models.model_user as model_user
import schemas.schema_vehicle as schema_vehicle
import crud.crud_vehicle as crud
from routes.routes_auth import get_current_user
from typing import List

# 👇 IMPORTANTE: Importar crud_user para validar usuarios
import crud.crud_user as crud_user

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schema_vehicle.Vehiculo])
def read_vehicles(
    skip: int = 0, 
    limit: int = 100, 
    current_user: model_user.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return crud.get_vehicles(db=db, skip=skip, limit=limit)


@router.get("/{vehicle_id}")
def read_vehicle(
    vehicle_id: int, 
    current_user: model_user.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    veh = crud.get_vehicle_by_id(db=db, vehicle_id=vehicle_id)
    if not veh:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return veh


@router.post("/", status_code=201)
def create_vehicle(
    vehicle: schema_vehicle.VehiculoCreate, 
    current_user: model_user.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # 👇 USAR crud_user.get_user_by_id en lugar de crud.get_user_by_id
    propietario = crud_user.get_user_by_id(db, vehicle.usuario_Id)
    if not propietario:
        raise HTTPException(
            status_code=400, 
            detail=f"Usuario (propietario) con id {vehicle.usuario_Id} no existe"
        )
    
    return crud.create_vehicle(db=db, vehicle=vehicle)


@router.put("/{vehicle_id}")
def update_vehicle(
    vehicle_id: int, 
    vehicle: schema_vehicle.VehiculoUpdate, 
    current_user: model_user.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_veh = crud.update_vehicle(db=db, vehicle_id=vehicle_id, vehicle=vehicle)
    if not db_veh:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_veh


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(
    vehicle_id: int, 
    current_user: model_user.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_veh = crud.delete_vehicle(db=db, vehicle_id=vehicle_id)
    if not db_veh:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"ok": True}