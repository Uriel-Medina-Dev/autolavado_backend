'''contendra el crud de vehiculos'''
import models.model_vehicle
import schemas.schema_vehicle
from sqlalchemy.orm import Session

def get_vehicles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.model_vehicle.Vehicle).offset(skip).limit(limit).all()

def get_vehicle_by_id(db: Session, vehicle_id: int):
    return db.query(models.model_vehicle.Vehicle).filter(models.model_vehicle.Vehicle.Id == vehicle_id).first()

def create_vehicle(db: Session, vehicle: schemas.schema_vehicle.VehiculoCreate):
    db_vehicle = models.model_vehicle.Vehicle(
        usuario_Id=vehicle.usuario_Id,
        placa=vehicle.placa,
        modelo=vehicle.modelo,
        serie=vehicle.serie,
        color=vehicle.color,
        tipo=vehicle.tipo,
        anio=vehicle.anio,
        estado=vehicle.estado,
        fecha_registro=vehicle.fecha_registro,
        fecha_actualizacion=vehicle.fecha_actualizacion
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def update_vehicle(db: Session, vehicle_id: int, vehicle: schemas.schema_vehicle.VehiculoUpdate):
    db_vehicle = db.query(models.model_vehicle.Vehicle).filter(models.model_vehicle.Vehicle.Id == vehicle_id).first()
    if db_vehicle:
        for field, value in vehicle.dict(exclude_unset=True).items():
            setattr(db_vehicle, field, value)
        db.commit()
        db.refresh(db_vehicle)
    return db_vehicle

def delete_vehicle(db: Session, vehicle_id: int):
    db_vehicle = db.query(models.model_vehicle.Vehicle).filter(models.model_vehicle.Vehicle.Id == vehicle_id).first()
    if db_vehicle:
        db.delete(db_vehicle)
        db.commit()
    return db_vehicle