from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import config.db
import models.model_user as model_user
import schemas.schema_inventario as schema_inventario
import crud.crud_inventario as crud_inventario
import crud.crud_producto as crud_producto
from routes.routes_auth import get_current_user

router = APIRouter(prefix="/inventario", tags=["Inventario"])


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/movimientos", response_model=List[dict])
def get_movimientos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    producto_id: Optional[int] = None,
    tipo: Optional[str] = Query(None, pattern="^(Entrada|Salida|Ajuste|Devolución|Compra|Venta)$"),
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    usuario_id: Optional[int] = None,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener movimientos de inventario con filtros"""
    return crud_inventario.get_movimientos_con_detalles(
        db=db,
        skip=skip,
        limit=limit,
        producto_id=producto_id
    )


@router.get("/movimientos/{movimiento_id}", response_model=dict)
def get_movimiento(
    movimiento_id: int,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un movimiento por ID"""
    movimientos = crud_inventario.get_movimientos_con_detalles(db=db, limit=1000)
    for m in movimientos:
        if m["id"] == movimiento_id:
            return m
    raise HTTPException(status_code=404, detail="Movimiento no encontrado")


@router.post("/movimientos", status_code=201, response_model=schema_inventario.Inventario)
def crear_movimiento(
    movimiento: schema_inventario.MovimientoStock,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registrar un nuevo movimiento de inventario"""
    # Verificar que el producto existe
    producto = crud_producto.get_producto_by_id(db, movimiento.producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Registrar movimiento
    result = crud_inventario.registrar_movimiento(
        db=db,
        movimiento=movimiento,
        usuario_id=current_user.Id
    )
    
    if not result:
        if movimiento.tipo_movimiento in ["Salida", "Venta"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuficiente. Stock actual: {producto.stock_actual}"
            )
        else:
            raise HTTPException(status_code=400, detail="Error al registrar movimiento")
    
    return result


@router.put("/movimientos/{movimiento_id}", response_model=schema_inventario.Inventario)
def actualizar_movimiento(
    movimiento_id: int,
    movimiento: schema_inventario.InventarioUpdate,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un movimiento (solo concepto, referencia, notas)"""
    db_movimiento = crud_inventario.update_movimiento(
        db=db,
        movimiento_id=movimiento_id,
        movimiento=movimiento
    )
    
    if not db_movimiento:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    
    return db_movimiento


@router.delete("/movimientos/{movimiento_id}", status_code=200)
def eliminar_movimiento(
    movimiento_id: int,
    hard_delete: bool = Query(False, description="True para eliminar físicamente"),
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un movimiento (NO revierte el stock)"""
    db_movimiento = crud_inventario.delete_movimiento(
        db=db,
        movimiento_id=movimiento_id,
        hard_delete=hard_delete
    )
    
    if not db_movimiento:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    
    return {
        "message": f"Movimiento {'eliminado físicamente' if hard_delete else 'desactivado'} exitosamente",
        "id": movimiento_id
    }


@router.get("/resumen")
def get_resumen_inventario(
    producto_id: Optional[int] = None,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen de inventario por producto"""
    return crud_inventario.get_resumen_por_producto(db=db, producto_id=producto_id)


@router.get("/movimientos-por-dia")
def get_movimientos_por_dia(
    dias: int = Query(30, ge=1, le=90),
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener movimientos agrupados por día"""
    return crud_inventario.get_movimientos_por_dia(db=db, dias=dias)


@router.post("/entrada", status_code=201)
def registrar_entrada(
    producto_id: int = Query(...),
    cantidad: int = Query(..., gt=0),
    concepto: str = Query("Compra de producto"),
    referencia: Optional[str] = None,
    notas: Optional[str] = None,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registrar una entrada de stock"""
    movimiento = schema_inventario.MovimientoStock(
        producto_id=producto_id,
        tipo_movimiento="Entrada",
        cantidad=cantidad,
        concepto=concepto,
        referencia=referencia,
        notas=notas
    )
    
    result = crud_inventario.registrar_movimiento(
        db=db,
        movimiento=movimiento,
        usuario_id=current_user.Id
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="Error al registrar entrada")
    
    return {
        "message": "Entrada registrada exitosamente",
        "movimiento_id": result.Id,
        "nuevo_stock": result.stock_nuevo
    }


@router.post("/salida", status_code=201)
def registrar_salida(
    producto_id: int = Query(...),
    cantidad: int = Query(..., gt=0),
    concepto: str = Query("Venta de producto"),
    referencia: Optional[str] = None,
    notas: Optional[str] = None,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registrar una salida de stock"""
    # Verificar stock suficiente
    producto = crud_producto.get_producto_by_id(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if producto.stock_actual < cantidad:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Disponible: {producto.stock_actual}"
        )
    
    movimiento = schema_inventario.MovimientoStock(
        producto_id=producto_id,
        tipo_movimiento="Salida",
        cantidad=cantidad,
        concepto=concepto,
        referencia=referencia,
        notas=notas
    )
    
    result = crud_inventario.registrar_movimiento(
        db=db,
        movimiento=movimiento,
        usuario_id=current_user.Id
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="Error al registrar salida")
    
    return {
        "message": "Salida registrada exitosamente",
        "movimiento_id": result.Id,
        "nuevo_stock": result.stock_nuevo
    }


@router.post("/ajuste", status_code=201)
def realizar_ajuste(
    producto_id: int = Query(...),
    nuevo_stock: int = Query(..., ge=0),
    motivo: str = Query("Ajuste de inventario"),
    notas: Optional[str] = None,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Realizar un ajuste de stock (establecer un nuevo stock manualmente)"""
    producto = crud_producto.get_producto_by_id(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    movimiento = schema_inventario.MovimientoStock(
        producto_id=producto_id,
        tipo_movimiento="Ajuste",
        cantidad=nuevo_stock,  # En ajuste, cantidad es el nuevo stock deseado
        concepto=motivo,
        notas=notas
    )
    
    result = crud_inventario.registrar_movimiento(
        db=db,
        movimiento=movimiento,
        usuario_id=current_user.Id
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="Error al realizar ajuste")
    
    diferencia = result.stock_nuevo - result.stock_anterior
    return {
        "message": "Ajuste realizado exitosamente",
        "movimiento_id": result.Id,
        "stock_anterior": result.stock_anterior,
        "stock_nuevo": result.stock_nuevo,
        "diferencia": diferencia
    }