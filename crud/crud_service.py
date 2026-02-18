'''contendra el crud de servicios'''
import models.model_service
import schemas.schema_services
from sqlalchemy.orm import Session

def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.model_service.Servicios).offset(skip).limit(limit).all()

def get_service_by_id(db: Session, service_id: int):
    return db.query(models.model_service.Servicios).filter(models.model_service.Servicios.Id == service_id).first()

def create_service(db: Session, service: schemas.schema_services.ServicioCreate):
    db_service = models.model_service.Servicios(
        nombre=service.nombre,
        descripcion=service.descripcion,
        costo=service.costo,
        duracion_minutos=service.duracion_minutos,
        estado=service.estado,
        fecha_registro=service.fecha_registro,
        fecha_actualizacion=service.fecha_actualizacion
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def update_service(db: Session, service_id: int, service: schemas.schema_services.ServicioUpdate):
    db_service = db.query(models.model_service.Servicios).filter(models.model_service.Servicios.Id == service_id).first()
    if db_service:
        for field, value in service.dict(exclude_unset=True).items():
            setattr(db_service, field, value)
        db.commit()
        db.refresh(db_service)
    return db_service

def delete_service(db: Session, service_id: int):
    db_service = db.query(models.model_service.Servicios).filter(models.model_service.Servicios.Id == service_id).first()
    if db_service:
        db.delete(db_service)
        db.commit()
    return db_service