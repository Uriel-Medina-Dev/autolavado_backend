from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import config.db
import models.model_user as model_user
import schemas.schema_producto as schema_producto
import crud.crud_producto as crud
from routes.routes_auth import get_current_user

router = APIRouter(prefix="/productos", tags=["Productos"])


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schema_producto.Producto])
def read_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: bool = True,
    categoria: Optional[str] = None,
    stock_bajo: bool = False,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de productos con filtros opcionales"""
    return crud.get_productos(
        db=db, 
        skip=skip, 
        limit=limit,
        solo_activos=solo_activos,
        categoria=categoria,
        stock_bajo=stock_bajo
    )


@router.get("/search", response_model=List[schema_producto.Producto])
def search_productos(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar productos por nombre, código o descripción"""
    return crud.search_productos(db=db, search_term=q, limit=limit)


@router.get("/bajo-stock", response_model=List[schema_producto.Producto])
def productos_bajo_stock(
    limit: int = Query(50, ge=1),
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener productos con stock por debajo del mínimo"""
    return crud.get_productos_bajo_stock(db=db, limit=limit)


@router.get("/resumen-stock")
def resumen_stock(
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen de stock (totales y valor)"""
    return crud.get_resumen_stock(db=db)


@router.get("/{producto_id}", response_model=schema_producto.Producto)
def read_producto(
    producto_id: int,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un producto por ID"""
    db_producto = crud.get_producto_by_id(db=db, producto_id=producto_id)
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Agregar nombre del usuario que registró
    if db_producto.usuario_registro:
        db_producto.usuario_registro_nombre = db_producto.usuario_registro.user
    
    return db_producto


@router.get("/codigo/{codigo}", response_model=schema_producto.Producto)
def read_producto_by_codigo(
    codigo: str,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un producto por su código único"""
    db_producto = crud.get_producto_by_codigo(db=db, codigo=codigo)
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto


@router.post("/", status_code=201, response_model=schema_producto.Producto)
def create_producto(
    producto: schema_producto.ProductoCreate,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo producto"""
    # Verificar si ya existe un producto con el mismo código
    existing = crud.get_producto_by_codigo(db=db, codigo=producto.codigo)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Ya existe un producto con el código '{producto.codigo}'"
        )
    
    # Validación adicional: precio venta >= precio compra
    if producto.precio_venta < producto.precio_compra:
        raise HTTPException(
            status_code=400,
            detail="El precio de venta no puede ser menor al precio de compra"
        )
    
    return crud.create_producto(db=db, producto=producto, usuario_id=current_user.Id)


@router.put("/{producto_id}", response_model=schema_producto.Producto)
def update_producto(
    producto_id: int,
    producto: schema_producto.ProductoUpdate,
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un producto existente"""
    # Verificar si el producto existe
    db_producto = crud.get_producto_by_id(db=db, producto_id=producto_id)
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Si se actualiza el código, verificar que no esté duplicado
    if producto.codigo and producto.codigo != db_producto.codigo:
        existing = crud.get_producto_by_codigo(db=db, codigo=producto.codigo)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe otro producto con el código '{producto.codigo}'"
            )
    
    return crud.update_producto(db=db, producto_id=producto_id, producto=producto)


@router.patch("/{producto_id}/stock")
def ajustar_stock(
    producto_id: int,
    cantidad: int = Query(..., description="Cantidad a ajustar"),
    # CORREGIDO: pattern en lugar de regex
    operacion: str = Query("sumar", pattern="^(sumar|restar)$"),
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ajustar el stock de un producto (sumar o restar)"""
    es_suma = operacion == "sumar"
    
    result = crud.ajustar_stock(
        db=db, 
        producto_id=producto_id, 
        cantidad=cantidad, 
        es_suma=es_suma
    )
    
    if not result:
        if not es_suma:
            raise HTTPException(status_code=400, detail="Stock insuficiente")
        else:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return {
        "message": f"Stock {'aumentado' if es_suma else 'disminuido'} exitosamente",
        "producto_id": producto_id,
        "stock_actual": result.stock_actual
    }


@router.delete("/{producto_id}", status_code=200)
def delete_producto(
    producto_id: int,
    hard_delete: bool = Query(False, description="True para eliminar físicamente"),
    current_user: model_user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un producto (lógica o físicamente)"""
    db_producto = crud.delete_producto(
        db=db, 
        producto_id=producto_id, 
        hard_delete=hard_delete
    )
    
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return {
        "message": f"Producto {'eliminado físicamente' if hard_delete else 'desactivado'} exitosamente",
        "producto_id": producto_id
    }