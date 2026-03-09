"""contendra el crud de productos"""
from sqlalchemy.orm import Session
from models.model_producto import Producto
from models.model_inventario import Inventario, TipoMovimiento
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
        Producto.nombre.ilike(f"%{search_term}%") |
        Producto.codigo.ilike(f"%{search_term}%") |
        Producto.descripcion.ilike(f"%{search_term}%")
    ).limit(limit).all()


def create_producto(db: Session, producto: ProductoCreate, usuario_id: Optional[int] = None):
    """Crear un nuevo producto y registrar movimiento inicial en inventario"""
    
    # Crear el producto
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
    db.flush()  # Para obtener el ID del producto sin commitear aún
    
    # 👇 REGISTRAR MOVIMIENTO INICIAL EN INVENTARIO
    if producto.stock_actual > 0:
        movimiento_inventario = Inventario(
            producto_id=db_producto.Id,
            tipo_movimiento=TipoMovimiento.ENTRADA,
            cantidad=producto.stock_actual,
            stock_anterior=0,
            stock_nuevo=producto.stock_actual,
            concepto="Stock inicial",
            referencia="CREACIÓN",
            notas=f"Stock inicial al crear el producto {producto.nombre}",
            usuario_id=usuario_id or producto.usuario_registro_id,
            fecha_registro=datetime.now(),
            fecha_actualizacion=datetime.now()
        )
        db.add(movimiento_inventario)
    
    db.commit()
    db.refresh(db_producto)
    return db_producto


def update_producto(db: Session, producto_id: int, producto: ProductoUpdate, usuario_id: Optional[int] = None):
    """Actualizar un producto existente"""
    db_producto = db.query(Producto).filter(Producto.Id == producto_id).first()
    if db_producto:
        # Guardar stock anterior para posible registro
        stock_anterior = db_producto.stock_actual
        
        update_data = producto.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_producto, field, value)
        
        db_producto.fecha_actualizacion = datetime.now()
        
        # 👇 Si se actualizó el stock, registrar movimiento
        if 'stock_actual' in update_data and update_data['stock_actual'] != stock_anterior:
            diferencia = update_data['stock_actual'] - stock_anterior
            tipo = TipoMovimiento.ENTRADA if diferencia > 0 else TipoMovimiento.SALIDA
            
            movimiento_inventario = Inventario(
                producto_id=db_producto.Id,
                tipo_movimiento=tipo,
                cantidad=abs(diferencia),
                stock_anterior=stock_anterior,
                stock_nuevo=update_data['stock_actual'],
                concepto="Actualización manual",
                referencia="UPDATE",
                notas=f"Actualización de stock vía PUT",
                usuario_id=usuario_id,
                fecha_registro=datetime.now(),
                fecha_actualizacion=datetime.now()
            )
            db.add(movimiento_inventario)
        
        db.commit()
        db.refresh(db_producto)
    return db_producto


def delete_producto(db: Session, producto_id: int, hard_delete: bool = False):
    """Eliminar un producto (lógica o físicamente)"""
    db_producto = db.query(Producto).filter(Producto.Id == producto_id).first()
    if db_producto:
        if hard_delete:
            db.delete(db_producto)
        else:
            db_producto.estado = False
            db_producto.fecha_actualizacion = datetime.now()
        db.commit()
    return db_producto


def ajustar_stock(db: Session, producto_id: int, cantidad: int, es_suma: bool = True, usuario_id: Optional[int] = None):
    """
    Ajustar el stock de un producto
    - cantidad: número a sumar o restar
    - es_suma: True para sumar, False para restar
    """
    db_producto = db.query(Producto).filter(Producto.Id == producto_id).first()
    if db_producto:
        stock_anterior = db_producto.stock_actual
        
        if es_suma:
            db_producto.stock_actual += cantidad
            tipo = TipoMovimiento.ENTRADA
        else:
            if db_producto.stock_actual >= cantidad:
                db_producto.stock_actual -= cantidad
                tipo = TipoMovimiento.SALIDA
            else:
                return None  # Stock insuficiente
        
        db_producto.fecha_actualizacion = datetime.now()
        
        # 👇 Registrar movimiento en inventario
        movimiento = Inventario(
            producto_id=db_producto.Id,
            tipo_movimiento=tipo,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=db_producto.stock_actual,
            concepto="Ajuste manual",
            referencia="AJUSTE",
            notas=f"Ajuste de stock vía función",
            usuario_id=usuario_id,
            fecha_registro=datetime.now(),
            fecha_actualizacion=datetime.now()
        )
        db.add(movimiento)
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
        "valor_inventario": round(valor_inventario, 2),
        "productos_bajo_stock": productos_bajo_stock
    }