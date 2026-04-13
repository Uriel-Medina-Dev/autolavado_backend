"""contendra el crud de servicios"""
from sqlalchemy.orm import Session
from models.model_service import Servicios
from schemas.schema_services import ServicioCreate, ServicioUpdate
from datetime import datetime


def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Servicios).offset(skip).limit(limit).all()


def get_service_by_id(db: Session, service_id: int):
    return db.query(Servicios).filter(Servicios.Id == service_id).first()


def create_service(db: Session, service: ServicioCreate):
    """Crear un nuevo servicio - las fechas se asignan automáticamente"""
    db_service = Servicios(
        nombre=service.nombre,
        descripcion=service.descripcion,
        costo=service.costo,
        duracion_minutos=service.duracion_minutos,
        estado=service.estado,
        # Las fechas NO se toman del request, se asignan automáticamente
        fecha_registro=datetime.now(),  # Fecha actual
        fecha_actualizacion=datetime.now()  # Fecha actual
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


def update_service(db: Session, service_id: int, service: ServicioUpdate):
    db_service = db.query(Servicios).filter(Servicios.Id == service_id).first()
    if db_service:
        # Actualizar solo los campos proporcionados
        update_data = service.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_service, field, value)
        
        # Actualizar la fecha de modificación
        db_service.fecha_actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_service)
    return db_service


def delete_service(db: Session, service_id: int):
    db_service = db.query(Servicios).filter(Servicios.Id == service_id).first()
    if db_service:
        db.delete(db_service)
        db.commit()
    return db_service