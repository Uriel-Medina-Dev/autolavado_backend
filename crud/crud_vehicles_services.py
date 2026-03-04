"""contendra el crud de vehiculos servicios"""
from sqlalchemy.orm import Session
from models.model_vehicles_services import VehiculoServicio
from schemas.schema_vehicles_services import UsuariosVehiculoServicioCreate, UsuariosVehiculoServicioUpdate
from datetime import datetime


def get_vehicles_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(VehiculoServicio).offset(skip).limit(limit).all()


def get_vehicle_service_by_id(db: Session, vs_id: int):
    return db.query(VehiculoServicio).filter(VehiculoServicio.Id == vs_id).first()


def create_vehicle_service(db: Session, vs: UsuariosVehiculoServicioCreate):
    """Crear una nueva asignación - las fechas se asignan automáticamente"""
    db_vs = VehiculoServicio(
        vehicle_Id=vs.vehicle_Id,
        cajero_Id=vs.cajero_Id,
        operativo_Id=vs.operativo_Id,
        servicio_Id=vs.servicio_Id,
        date=vs.date,
        time=vs.time,
        estatus=vs.estatus,
        estado=vs.estado,
        fecha_registro=datetime.now(),  # Fecha actual
        fecha_actualizacion=datetime.now()  # Fecha actual
    )
    db.add(db_vs)
    db.commit()
    db.refresh(db_vs)
    return db_vs


def update_vehicle_service(db: Session, vs_id: int, vs: UsuariosVehiculoServicioUpdate):
    db_vs = db.query(VehiculoServicio).filter(VehiculoServicio.Id == vs_id).first()
    if db_vs:
        update_data = vs.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vs, field, value)
        
        # Actualizar fecha de modificación
        db_vs.fecha_actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_vs)
    return db_vs


def delete_vehicle_service(db: Session, vs_id: int):
    db_vs = db.query(VehiculoServicio).filter(VehiculoServicio.Id == vs_id).first()
    if db_vs:
        db.delete(db_vs)
        db.commit()
    return db_vs