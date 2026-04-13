from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import config.db
import models.model_user as model_user
import schemas.schema_cajero as schema_cajero
import crud.crud_cajero as crud_cajero
import crud.crud_user as crud_user
from routes.routes_auth import get_current_user

router = APIRouter(prefix="/cajeros", tags=["Cajeros"])


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schema_cajero.Cajero])
def read_cajeros(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = True,
    turno: Optional[str] = Query(None, pattern="^(Matutino|Vespertino|Nocturno)$"),
    con_caja_asignada: Optional[bool] = None,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de cajeros con filtros opcionales"""
    cajeros = crud_cajero.get_cajeros(
        db=db, 
        skip=skip, 
        limit=limit,
        solo_activos=solo_activos,
        turno=turno,
        con_caja_asignada=con_caja_asignada
    )
    
    # Enriquecer con datos del usuario
    result = []
    for cajero in cajeros:
        usuario = crud_user.get_user_by_id(db, cajero.usuario_id)
        if usuario:
            cajero.usuario_nombre_completo = f"{usuario.user_name} {usuario.user_1lastname} {usuario.user_2lastname or ''}".strip()
            cajero.usuario_user = usuario.user
            cajero.usuario_telefono = usuario.user_phone
        result.append(cajero)
    
    return result


@router.get("/disponibles", response_model=List[schema_cajero.Cajero])
def read_cajeros_disponibles(
    turno: Optional[str] = Query(None, pattern="^(Matutino|Vespertino|Nocturno)$"),
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener cajeros disponibles (sin caja asignada)"""
    return crud_cajero.get_cajeros_disponibles(db=db, turno=turno)


@router.get("/por-turno")
def get_cajeros_por_turno(
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de cajeros por turno"""
    return crud_cajero.get_cajeros_por_turno(db=db)


@router.get("/{cajero_id}", response_model=schema_cajero.CajeroConUsuario)
def read_cajero(
    cajero_id: int,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un cajero por ID con información completa"""
    db_cajero = crud_cajero.get_cajero_by_id(db=db, cajero_id=cajero_id)
    if not db_cajero:
        raise HTTPException(status_code=404, detail="Cajero no encontrado")
    
    # Agregar información del usuario
    usuario = crud_user.get_user_by_id(db, db_cajero.usuario_id)
    if usuario:
        db_cajero.usuario_info = {
            "id": usuario.Id,
            "nombre_completo": f"{usuario.user_name} {usuario.user_1lastname} {usuario.user_2lastname or ''}".strip(),
            "username": usuario.user,
            "telefono": usuario.user_phone,
            "email": usuario.user,
            "rol_id": usuario.rol_Id
        }
    
    return db_cajero


@router.get("/usuario/{usuario_id}", response_model=schema_cajero.Cajero)
def read_cajero_by_usuario(
    usuario_id: int,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener cajero por ID de usuario"""
    db_cajero = crud_cajero.get_cajero_by_usuario_id(db=db, usuario_id=usuario_id)
    if not db_cajero:
        raise HTTPException(status_code=404, detail="Cajero no encontrado para este usuario")
    return db_cajero


@router.post("/", status_code=201, response_model=schema_cajero.Cajero)
def create_cajero(
    cajero: schema_cajero.CajeroCreate,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo cajero"""
    # Verificar que el usuario existe
    usuario = crud_user.get_user_by_id(db, cajero.usuario_id)
    if not usuario:
        raise HTTPException(status_code=400, detail="El usuario especificado no existe")
    
    # Verificar que el usuario tiene rol de cajero (rol_id = 2)
    if usuario.rol_Id != 2:
        raise HTTPException(status_code=400, detail="El usuario no tiene rol de cajero (rol_id=2)")
    
    # Verificar que el usuario no sea ya cajero
    existing = crud_cajero.get_cajero_by_usuario_id(db=db, usuario_id=cajero.usuario_id)
    if existing:
        raise HTTPException(status_code=400, detail="Este usuario ya está registrado como cajero")
    
    # Verificar número de empleado único
    existing = crud_cajero.get_cajero_by_numero_empleado(db=db, numero_empleado=cajero.numero_empleado)
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un cajero con este número de empleado")
    
    return crud_cajero.create_cajero(db=db, cajero=cajero)


@router.put("/{cajero_id}", response_model=schema_cajero.Cajero)
def update_cajero(
    cajero_id: int,
    cajero: schema_cajero.CajeroUpdate,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un cajero existente"""
    db_cajero = crud_cajero.get_cajero_by_id(db=db, cajero_id=cajero_id)
    if not db_cajero:
        raise HTTPException(status_code=404, detail="Cajero no encontrado")
    
    return crud_cajero.update_cajero(db=db, cajero_id=cajero_id, cajero=cajero)


@router.patch("/{cajero_id}/asignar-caja")
def asignar_caja(
    cajero_id: int,
    asignacion: schema_cajero.AsignarCaja,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Asignar una caja a un cajero"""
    db_cajero = crud_cajero.get_cajero_by_id(db=db, cajero_id=cajero_id)
    if not db_cajero:
        raise HTTPException(status_code=404, detail="Cajero no encontrado")
    
    result = crud_cajero.asignar_caja(db=db, cajero_id=cajero_id, numero_caja=asignacion.numero_caja)
    
    return {
        "message": f"Caja {asignacion.numero_caja} asignada exitosamente",
        "cajero_id": cajero_id,
        "numero_caja": result.numero_caja
    }


@router.patch("/{cajero_id}/desasignar-caja")
def desasignar_caja(
    cajero_id: int,
    motivo: Optional[str] = Query(None, max_length=200),
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desasignar la caja de un cajero"""
    db_cajero = crud_cajero.get_cajero_by_id(db=db, cajero_id=cajero_id)
    if not db_cajero:
        raise HTTPException(status_code=404, detail="Cajero no encontrado")
    
    result = crud_cajero.desasignar_caja(db=db, cajero_id=cajero_id)
    
    return {
        "message": "Caja desasignada exitosamente",
        "cajero_id": cajero_id,
        "motivo": motivo
    }


@router.patch("/{cajero_id}/cambiar-turno")
def cambiar_turno(
    cajero_id: int,
    cambio: schema_cajero.CambioTurno,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar el turno de un cajero"""
    db_cajero = crud_cajero.get_cajero_by_id(db=db, cajero_id=cajero_id)
    if not db_cajero:
        raise HTTPException(status_code=404, detail="Cajero no encontrado")
    
    result = crud_cajero.cambiar_turno(db=db, cajero_id=cajero_id, nuevo_turno=cambio.turno)
    
    return {
        "message": f"Turno cambiado a {cambio.turno} exitosamente",
        "cajero_id": cajero_id,
        "nuevo_turno": result.turno,
        "motivo": cambio.motivo
    }


@router.delete("/{cajero_id}", status_code=200)
def delete_cajero(
    cajero_id: int,
    hard_delete: bool = Query(False, description="True para eliminar físicamente"),
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un cajero (lógica o físicamente)"""
    db_cajero = crud_cajero.delete_cajero(
        db=db, 
        cajero_id=cajero_id, 
        hard_delete=hard_delete
    )
    
    if not db_cajero:
        raise HTTPException(status_code=404, detail="Cajero no encontrado")
    
    return {
        "message": f"Cajero {'eliminado físicamente' if hard_delete else 'desactivado'} exitosamente",
        "cajero_id": cajero_id
    }