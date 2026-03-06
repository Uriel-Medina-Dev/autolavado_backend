from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import config.db
import models.model_user as model_user
import schemas.schema_vehicles_services as schema_vs
import crud.crud_vehicles_services as crud
from routes.routes_auth import get_current_user
from datetime import datetime

# Imports para validaciones
import crud.crud_vehicle as crud_vehicle
import crud.crud_user as crud_user
import crud.crud_service as crud_service

router = APIRouter(prefix="/vehicle_services", tags=["VehicleServices"])


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============= ENDPOINTS EXISTENTES =============

@router.get("/", response_model=List[schema_vs.UsuariosVehiculoServicio])
def read_vs(
    skip: int = 0, 
    limit: int = 100, 
    current_user: model_user.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Obtener lista de asignaciones básicas"""
    return crud.get_vehicles_services(db=db, skip=skip, limit=limit)


@router.get("/{vs_id}", response_model=schema_vs.UsuariosVehiculoServicio)
def read_vs_item(
    vs_id: int, 
    current_user: model_user.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Obtener una asignación por ID"""
    item = crud.get_vehicle_service_by_id(db=db, vs_id=vs_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", status_code=201, response_model=schema_vs.UsuariosVehiculoServicio)
def create_vs(
    item: schema_vs.UsuariosVehiculoServicioCreate, 
    current_user: model_user.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Crear una nueva asignación"""
    # Validar vehículo
    if not crud_vehicle.get_vehicle_by_id(db, item.vehicle_Id):
        raise HTTPException(status_code=400, detail="Vehículo no existe")
    
    # Validar cajero
    if not crud_user.get_user_by_id(db, item.cajero_Id):
        raise HTTPException(status_code=400, detail="Usuario cajero no existe")
    
    # Validar operativo
    if not crud_user.get_user_by_id(db, item.operativo_Id):
        raise HTTPException(status_code=400, detail="Usuario operativo no existe")
    
    # Validar servicio
    if not crud_service.get_service_by_id(db, item.servicio_Id):
        raise HTTPException(status_code=400, detail="Servicio no existe")
    
    return crud.create_vehicle_service(db=db, vs=item)


@router.put("/{vs_id}", response_model=schema_vs.UsuariosVehiculoServicio)
def update_vs(
    vs_id: int, 
    item: schema_vs.UsuariosVehiculoServicioUpdate, 
    current_user: model_user.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Actualizar una asignación existente"""
    db_item = crud.update_vehicle_service(db=db, vs_id=vs_id, vs=item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.delete("/{vs_id}", status_code=200)
def delete_vs(
    vs_id: int, 
    current_user: model_user.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Eliminar una asignación"""
    db_item = crud.delete_vehicle_service(db=db, vs_id=vs_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Asignación eliminada exitosamente", "id": vs_id}


# ============= NUEVOS ENDPOINTS CON JOINS =============

@router.get("/completas/", response_model=List[dict])
def get_asignaciones_completas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    estatus: Optional[str] = Query(None, pattern="^(Programada|Proceso|Realizada|Cancelada)$"),
    cajero_id: Optional[int] = None,
    vehiculo_id: Optional[int] = None,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener asignaciones con información completa:
    - Datos del vehículo (placa, modelo, color)
    - Datos del propietario (nombre, teléfono)
    - Datos del cajero que atendió
    - Datos del operativo que realizó el servicio
    - Datos del servicio (nombre, precio original)
    - Precio final con descuento aplicado
    """
    return crud_completo.get_asignaciones_completas(
        db=db,
        skip=skip,
        limit=limit,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estatus=estatus,
        cajero_id=cajero_id,
        vehiculo_id=vehiculo_id
    )


@router.get("/completas/{asignacion_id}", response_model=dict)
def get_asignacion_completa(
    asignacion_id: int,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una asignación completa por ID"""
    result = crud_completo.get_asignacion_completa_by_id(db=db, asignacion_id=asignacion_id)
    if not result:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return result


@router.get("/reportes/resumen-ventas", response_model=dict)
def get_resumen_ventas(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen de ventas para un período específico"""
    return crud_completo.get_resumen_ventas(
        db=db,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


@router.get("/reportes/ventas-por-dia")
def get_ventas_por_dia(
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    año: int = Query(..., ge=2020, le=2100, description="Año"),
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener ventas agrupadas por día para un mes específico"""
    return crud_completo.get_ventas_por_dia(db=db, mes=mes, año=año)


@router.get("/estadisticas/cajero/{cajero_id}")
def get_estadisticas_cajero(
    cajero_id: int,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de ventas de un cajero específico"""
    asignaciones = crud_completo.get_asignaciones_completas(
        db=db,
        cajero_id=cajero_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limit=1000
    )
    
    total_ventas = sum(a["precio_final"] for a in asignaciones)
    total_servicios = len(asignaciones)
    descuentos_aplicados = sum(a["descuento"] for a in asignaciones if a["descuento"] > 0)
    
    return {
        "cajero_id": cajero_id,
        "cajero_nombre": asignaciones[0]["cajero_nombre"] if asignaciones else None,
        "total_servicios": total_servicios,
        "total_ventas": round(total_ventas, 2),
        "promedio_por_servicio": round(total_ventas / total_servicios, 2) if total_servicios > 0 else 0,
        "descuentos_aplicados": round(descuentos_aplicados, 2),
        "periodo": f"{fecha_inicio or 'inicio'} a {fecha_fin or 'hoy'}"
    }