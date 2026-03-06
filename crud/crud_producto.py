"""CRUD para productos"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.model_producto import Producto
from schemas.schema_producto import ProductoCreate, ProductoUpdate
from datetime import datetime
from typing import Optional, List


def get_productos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    solo_activos: bool = True,
    categoria: Optional[str] = None,
    stock_bajo: bool = False
):
    """Obtener productos con filtros opcionales"""
    query = db.query(Producto)
    
    if solo_activos:
        query = query.filter(Producto.estado == True)
    
    if categoria:
        query = query.filter(Producto.categoria == categoria)
    
    if stock_bajo:
        query = query.filter(Producto.stock_actual <= Producto.stock_minimo)
    
    return query.offset(skip).limit(limit).all()


def get_producto_by_id(db: Session, producto_id: int):
    """Obtener producto por ID"""
    return db.query(Producto).filter(Producto.Id == producto_id).first()


def get_producto_by_codigo(db: Session, codigo: str):
    """Obtener producto por código único"""
    return db.query(Producto).filter(Producto.codigo == codigo).first()


def search_productos(db: Session, search_term: str, limit: int = 20):
    """Buscar productos por nombre, código o descripción"""
    return db.query(Producto).filter(
        or_(
            Producto.nombre.ilike(f"%{search_term}%"),
            Producto.codigo.ilike(f"%{search_term}%"),
            Producto.descripcion.ilike(f"%{search_term}%")
        )
    ).limit(limit).all()


def create_producto(db: Session, producto: ProductoCreate, usuario_id: Optional[int] = None):
    """Crear un nuevo producto"""
    db_producto = Producto(
        codigo=producto.codigo,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        categoria=producto.categoria,
        precio_compra=producto.precio_compra,
        precio_venta=producto.precio_venta,
        stock_actual=producto.stock_actual,
        stock_minimo=producto.stock_minimo,
        unidad_medida=producto.unidad_medida,
        proveedor=producto.proveedor,
        ubicacion=producto.ubicacion,
        estado=producto.estado,
        usuario_registro_id=usuario_id or producto.usuario_registro_id,
        fecha_registro=datetime.now(),
        fecha_actualizacion=datetime.now()
    )
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


def update_producto(db: Session, producto_id: int, producto: ProductoUpdate):
    """Actualizar un producto existente"""
    db_producto = db.query(Producto).filter(Producto.Id == producto_id).first()
    if db_producto:
        update_data = producto.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_producto, field, value)
        
        db_producto.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_producto)
    return db_producto


def delete_producto(db: Session, producto_id: int, hard_delete: bool = False):
    """
    Eliminar un producto
    - hard_delete=True: Eliminación física de la BD
    - hard_delete=False: Eliminación lógica (cambiar estado a False)
    """
    db_producto = db.query(Producto).filter(Producto.Id == producto_id).first()
    if db_producto:
        if hard_delete:
            db.delete(db_producto)
        else:
            db_producto.estado = False
            db_producto.fecha_actualizacion = datetime.now()
        db.commit()
    return db_producto


def ajustar_stock(db: Session, producto_id: int, cantidad: int, es_suma: bool = True):
    """
    Ajustar el stock de un producto
    - cantidad: número a sumar o restar
    - es_suma: True para sumar, False para restar
    """
    db_producto = db.query(Producto).filter(Producto.Id == producto_id).first()
    if db_producto:
        if es_suma:
            db_producto.stock_actual += cantidad
        else:
            if db_producto.stock_actual >= cantidad:
                db_producto.stock_actual -= cantidad
            else:
                return None  # Stock insuficiente
        
        db_producto.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_producto)
    return db_producto


def get_productos_bajo_stock(db: Session, limit: int = 50):
    """Obtener productos con stock por debajo del mínimo"""
    return db.query(Producto).filter(
        Producto.estado == True,
        Producto.stock_actual <= Producto.stock_minimo
    ).limit(limit).all()


def get_resumen_stock(db: Session):
    """Obtener resumen de stock (totales)"""
    productos = db.query(Producto).filter(Producto.estado == True).all()
    
    total_productos = len(productos)
    total_stock = sum(p.stock_actual for p in productos)
    valor_inventario = sum(p.precio_compra * p.stock_actual for p in productos)
    productos_bajo_stock = sum(1 for p in productos if p.stock_actual <= p.stock_minimo)
    
    return {
        "total_productos": total_productos,
        "total_stock": total_stock,
        "valor_inventario": valor_inventario,
        "productos_bajo_stock": productos_bajo_stock
    }