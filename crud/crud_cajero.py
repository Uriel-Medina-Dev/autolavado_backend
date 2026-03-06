"""CRUD para cajeros"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.model_cajero import Cajero
from models.model_user import User
from schemas.schema_cajero import CajeroCreate, CajeroUpdate
from datetime import datetime, date
from typing import Optional, List


def get_cajeros(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    solo_activos: bool = True,
    turno: Optional[str] = None,
    con_caja_asignada: Optional[bool] = None
):
    """Obtener lista de cajeros con filtros opcionales"""
    query = db.query(Cajero).join(User, Cajero.usuario_id == User.Id)
    
    if solo_activos:
        query = query.filter(Cajero.estado == True, User.status == True)
    
    if turno:
        query = query.filter(Cajero.turno == turno)
    
    if con_caja_asignada is not None:
        if con_caja_asignada:
            query = query.filter(Cajero.numero_caja.isnot(None))
        else:
            query = query.filter(Cajero.numero_caja.is_(None))
    
    return query.offset(skip).limit(limit).all()


def get_cajero_by_id(db: Session, cajero_id: int):
    """Obtener cajero por ID"""
    return db.query(Cajero).filter(Cajero.Id == cajero_id).first()


def get_cajero_by_usuario_id(db: Session, usuario_id: int):
    """Obtener cajero por ID de usuario"""
    return db.query(Cajero).filter(Cajero.usuario_id == usuario_id).first()


def get_cajero_by_numero_empleado(db: Session, numero_empleado: str):
    """Obtener cajero por número de empleado"""
    return db.query(Cajero).filter(Cajero.numero_empleado == numero_empleado).first()


def get_cajeros_disponibles(db: Session, turno: Optional[str] = None):
    """Obtener cajeros disponibles (activos y sin caja asignada)"""
    query = db.query(Cajero).filter(
        Cajero.estado == True,
        Cajero.numero_caja.is_(None)
    )
    
    if turno:
        query = query.filter(Cajero.turno == turno)
    
    return query.all()


def create_cajero(db: Session, cajero: CajeroCreate):
    """Crear un nuevo cajero"""
    db_cajero = Cajero(
        usuario_id=cajero.usuario_id,
        numero_empleado=cajero.numero_empleado,
        turno=cajero.turno,
        numero_caja=cajero.numero_caja,
        fecha_contratacion=cajero.fecha_contratacion,
        salario=cajero.salario,
        contacto_emergencia_nombre=cajero.contacto_emergencia_nombre,
        contacto_emergencia_telefono=cajero.contacto_emergencia_telefono,
        contacto_emergencia_parentesco=cajero.contacto_emergencia_parentesco,
        banco=cajero.banco,
        cuenta_bancaria=cajero.cuenta_bancaria,
        clabe=cajero.clabe,
        estado=cajero.estado,
        fecha_registro=datetime.now(),
        fecha_actualizacion=datetime.now()
    )
    db.add(db_cajero)
    db.commit()
    db.refresh(db_cajero)
    return db_cajero


def update_cajero(db: Session, cajero_id: int, cajero: CajeroUpdate):
    """Actualizar un cajero existente"""
    db_cajero = db.query(Cajero).filter(Cajero.Id == cajero_id).first()
    if db_cajero:
        update_data = cajero.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cajero, field, value)
        
        db_cajero.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_cajero)
    return db_cajero


def delete_cajero(db: Session, cajero_id: int, hard_delete: bool = False):
    """Eliminar un cajero (lógica o físicamente)"""
    db_cajero = db.query(Cajero).filter(Cajero.Id == cajero_id).first()
    if db_cajero:
        if hard_delete:
            db.delete(db_cajero)
        else:
            db_cajero.estado = False
            db_cajero.fecha_actualizacion = datetime.now()
        db.commit()
    return db_cajero


def asignar_caja(db: Session, cajero_id: int, numero_caja: int):
    """Asignar una caja a un cajero"""
    db_cajero = db.query(Cajero).filter(Cajero.Id == cajero_id).first()
    if db_cajero:
        db_cajero.numero_caja = numero_caja
        db_cajero.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_cajero)
    return db_cajero


def desasignar_caja(db: Session, cajero_id: int):
    """Quitar la caja asignada a un cajero"""
    db_cajero = db.query(Cajero).filter(Cajero.Id == cajero_id).first()
    if db_cajero:
        db_cajero.numero_caja = None
        db_cajero.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_cajero)
    return db_cajero


def cambiar_turno(db: Session, cajero_id: int, nuevo_turno: str):
    """Cambiar el turno de un cajero"""
    db_cajero = db.query(Cajero).filter(Cajero.Id == cajero_id).first()
    if db_cajero:
        db_cajero.turno = nuevo_turno
        db_cajero.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_cajero)
    return db_cajero


def get_cajeros_por_turno(db: Session):
    """Obtener conteo de cajeros por turno"""
    cajeros = db.query(Cajero).filter(Cajero.estado == True).all()
    
    resultado = {
        "Matutino": 0,
        "Vespertino": 0,
        "Nocturno": 0,
        "total": len(cajeros)
    }
    
    for cajero in cajeros:
        if cajero.turno in resultado:
            resultado[cajero.turno] += 1
    
    return resultado


def get_cajeros_con_detalles(db: Session, skip: int = 0, limit: int = 100):
    """Obtener cajeros con información del usuario"""
    return db.query(
        Cajero, User
    ).join(
        User, Cajero.usuario_id == User.Id
    ).filter(
        Cajero.estado == True
    ).offset(skip).limit(limit).all()