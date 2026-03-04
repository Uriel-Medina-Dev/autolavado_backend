"""contendra el crud de vehiculos"""
from sqlalchemy.orm import Session
from models.model_vehicle import Vehicle
from schemas.schema_vehicle import VehiculoCreate, VehiculoUpdate
from datetime import datetime


def get_vehicles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Vehicle).offset(skip).limit(limit).all()


def get_vehicle_by_id(db: Session, vehicle_id: int):
    return db.query(Vehicle).filter(Vehicle.Id == vehicle_id).first()


def create_vehicle(db: Session, vehicle: VehiculoCreate):
    """Crear un nuevo vehículo - las fechas se asignan automáticamente"""
    db_vehicle = Vehicle(
        usuario_Id=vehicle.usuario_Id,
        placa=vehicle.placa,
        modelo=vehicle.modelo,
        serie=vehicle.serie,
        color=vehicle.color,
        tipo=vehicle.tipo,
        anio=vehicle.anio,
        estado=vehicle.estado,
        fecha_registro=datetime.now(),  # Fecha actual
        fecha_actualizacion=datetime.now()  # Fecha actual
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def update_vehicle(db: Session, vehicle_id: int, vehicle: VehiculoUpdate):
    db_vehicle = db.query(Vehicle).filter(Vehicle.Id == vehicle_id).first()
    if db_vehicle:
        update_data = vehicle.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vehicle, field, value)
        
        # Actualizar fecha de modificación
        db_vehicle.fecha_actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_vehicle)
    return db_vehicle


def delete_vehicle(db: Session, vehicle_id: int):
    db_vehicle = db.query(Vehicle).filter(Vehicle.Id == vehicle_id).first()
    if db_vehicle:
        db.delete(db_vehicle)
        db.commit()
    return db_vehicle