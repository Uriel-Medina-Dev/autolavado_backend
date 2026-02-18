'''contendra el crud de vehiculos servicios'''
import models.model_vehicles_services
import schemas.schema_vehicles_services
from sqlalchemy.orm import Session

def get_vehicles_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.model_vehicles_services.VehiculoServicio).offset(skip).limit(limit).all()

def get_vehicle_service_by_id(db: Session, vs_id: int):
    return db.query(models.model_vehicles_services.VehiculoServicio).filter(models.model_vehicles_services.VehiculoServicio.Id == vs_id).first()

def create_vehicle_service(db: Session, vs: schemas.schema_vehicles_services.UsuariosVehiculoServicioCreate):
    db_vs = models.model_vehicles_services.VehiculoServicio(
        vehicle_Id=vs.vehicle_Id,
        cajero_Id=vs.cajero_Id,
        operativo_Id=vs.operativo_Id,
        servicio_Id=vs.servicio_Id,
        date=vs.date,
        time=vs.time,
        estatus=vs.estatus,
        estado=vs.estado,
        fecha_registro=vs.fecha_registro,
        fecha_actualizacion=vs.fecha_actualizacion
    )
    db.add(db_vs)
    db.commit()
    db.refresh(db_vs)
    return db_vs

def update_vehicle_service(db: Session, vs_id: int, vs: schemas.schema_vehicles_services.UsuariosVehiculoServicioUpdate):
    db_vs = db.query(models.model_vehicles_services.VehiculoServicio).filter(models.model_vehicles_services.VehiculoServicio.Id == vs_id).first()
    if db_vs:
        for field, value in vs.dict(exclude_unset=True).items():
            setattr(db_vs, field, value)
        db.commit()
        db.refresh(db_vs)
    return db_vs

def delete_vehicle_service(db: Session, vs_id: int):
    db_vs = db.query(models.model_vehicles_services.VehiculoServicio).filter(models.model_vehicles_services.VehiculoServicio.Id == vs_id).first()
    if db_vs:
        db.delete(db_vs)
        db.commit()
    return db_vs