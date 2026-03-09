"""CRUD para movimientos de inventario"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from models.model_inventario import Inventario, TipoMovimiento
from models.model_producto import Producto
from models.model_user import User
from schemas.schema_inventario import InventarioCreate, InventarioUpdate, MovimientoStock
from datetime import datetime, date
from typing import List, Optional, Dict


def get_movimientos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    producto_id: Optional[int] = None,
    tipo: Optional[TipoMovimiento] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    usuario_id: Optional[int] = None
) -> List[Inventario]:
    """Obtener movimientos de inventario con filtros"""
    query = db.query(Inventario).filter(Inventario.estado == True)
    
    if producto_id:
        query = query.filter(Inventario.producto_id == producto_id)
    if tipo:
        query = query.filter(Inventario.tipo_movimiento == tipo)
    if fecha_inicio:
        query = query.filter(Inventario.fecha_registro >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Inventario.fecha_registro <= fecha_fin)
    if usuario_id:
        query = query.filter(Inventario.usuario_id == usuario_id)
    
    return query.order_by(Inventario.fecha_registro.desc()).offset(skip).limit(limit).all()


def get_movimiento_by_id(db: Session, movimiento_id: int) -> Optional[Inventario]:
    """Obtener un movimiento por ID"""
    return db.query(Inventario).filter(Inventario.Id == movimiento_id).first()


def get_movimientos_con_detalles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    producto_id: Optional[int] = None
) -> List[Dict]:
    """Obtener movimientos con información del producto y usuario"""
    query = db.query(
        Inventario,
        Producto.nombre.label("producto_nombre"),
        Producto.codigo.label("producto_codigo"),
        User.user_name.label("usuario_nombre"),
        User.user_1lastname.label("usuario_apellido")
    ).join(
        Producto, Inventario.producto_id == Producto.Id
    ).join(
        User, Inventario.usuario_id == User.Id
    ).filter(
        Inventario.estado == True
    )
    
    if producto_id:
        query = query.filter(Inventario.producto_id == producto_id)
    
    resultados = query.order_by(Inventario.fecha_registro.desc()).offset(skip).limit(limit).all()
    
    movimientos = []
    for r in resultados:
        movimientos.append({
            "id": r.Inventario.Id,
            "producto_id": r.Inventario.producto_id,
            "producto_nombre": r.producto_nombre,
            "producto_codigo": r.producto_codigo,
            "tipo_movimiento": r.Inventario.tipo_movimiento.value,
            "cantidad": r.Inventario.cantidad,
            "stock_anterior": r.Inventario.stock_anterior,
            "stock_nuevo": r.Inventario.stock_nuevo,
            "concepto": r.Inventario.concepto,
            "referencia": r.Inventario.referencia,
            "notas": r.Inventario.notas,
            "usuario_id": r.Inventario.usuario_id,
            "usuario_nombre": f"{r.usuario_nombre} {r.usuario_apellido or ''}".strip(),
            "fecha_registro": r.Inventario.fecha_registro
        })
    
    return movimientos


def registrar_movimiento(
    db: Session,
    movimiento: MovimientoStock,
    usuario_id: int
) -> Optional[Inventario]:
    """
    Registrar un movimiento de inventario y actualizar el stock del producto
    """
    # Verificar que el producto existe
    producto = db.query(Producto).filter(Producto.Id == movimiento.producto_id).first()
    if not producto:
        return None
    
    stock_anterior = producto.stock_actual
    stock_nuevo = stock_anterior
    
    # Calcular nuevo stock según tipo de movimiento
    if movimiento.tipo_movimiento in [TipoMovimiento.ENTRADA, TipoMovimiento.COMPRA, TipoMovimiento.DEVOLUCION]:
        stock_nuevo = stock_anterior + movimiento.cantidad
    elif movimiento.tipo_movimiento in [TipoMovimiento.SALIDA, TipoMovimiento.VENTA]:
        if stock_anterior < movimiento.cantidad:
            return None  # Stock insuficiente
        stock_nuevo = stock_anterior - movimiento.cantidad
    elif movimiento.tipo_movimiento == TipoMovimiento.AJUSTE:
        # En ajuste, la cantidad es el nuevo stock deseado
        stock_nuevo = movimiento.cantidad
        movimiento.cantidad = stock_nuevo - stock_anterior  # Diferencia real
    
    # Crear registro de inventario
    db_movimiento = Inventario(
        producto_id=movimiento.producto_id,
        tipo_movimiento=movimiento.tipo_movimiento,
        cantidad=abs(movimiento.cantidad),
        stock_anterior=stock_anterior,
        stock_nuevo=stock_nuevo,
        concepto=movimiento.concepto,
        referencia=movimiento.referencia,
        notas=movimiento.notas,
        usuario_id=usuario_id,
        fecha_registro=datetime.now(),
        fecha_actualizacion=datetime.now()
    )
    
    # Actualizar stock del producto
    producto.stock_actual = stock_nuevo
    producto.fecha_actualizacion = datetime.now()
    
    db.add(db_movimiento)
    db.commit()
    db.refresh(db_movimiento)
    
    return db_movimiento


def update_movimiento(
    db: Session,
    movimiento_id: int,
    movimiento: InventarioUpdate
) -> Optional[Inventario]:
    """Actualizar un movimiento (solo campos no críticos)"""
    db_movimiento = db.query(Inventario).filter(Inventario.Id == movimiento_id).first()
    if db_movimiento:
        update_data = movimiento.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_movimiento, field, value)
        
        db_movimiento.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_movimiento)
    return db_movimiento


def delete_movimiento(db: Session, movimiento_id: int, hard_delete: bool = False) -> Optional[Inventario]:
    """
    Eliminar un movimiento (lógica o físicamente)
    NOTA: Al eliminar un movimiento, NO se revierte el stock del producto
    """
    db_movimiento = db.query(Inventario).filter(Inventario.Id == movimiento_id).first()
    if db_movimiento:
        if hard_delete:
            db.delete(db_movimiento)
        else:
            db_movimiento.estado = False
            db_movimiento.fecha_actualizacion = datetime.now()
        db.commit()
    return db_movimiento


def get_resumen_por_producto(db: Session, producto_id: Optional[int] = None) -> List[Dict]:
    """Obtener resumen de inventario por producto"""
    query = db.query(
        Producto.Id,
        Producto.nombre,
        Producto.codigo,
        Producto.stock_actual,
        Producto.stock_minimo,
        func.coalesce(func.sum(
            func.case(
                (Inventario.tipo_movimiento.in_([TipoMovimiento.ENTRADA, TipoMovimiento.COMPRA, TipoMovimiento.DEVOLUCION]), 
                 Inventario.cantidad),
                else_=0
            )
        ), 0).label('total_entradas'),
        func.coalesce(func.sum(
            func.case(
                (Inventario.tipo_movimiento.in_([TipoMovimiento.SALIDA, TipoMovimiento.VENTA]), 
                 Inventario.cantidad),
                else_=0
            )
        ), 0).label('total_salidas'),
        func.max(Inventario.fecha_registro).label('ultimo_movimiento')
    ).outerjoin(
        Inventario, Producto.Id == Inventario.producto_id
    ).filter(
        Producto.estado == True
    ).group_by(
        Producto.Id, Producto.nombre, Producto.codigo, 
        Producto.stock_actual, Producto.stock_minimo
    )
    
    if producto_id:
        query = query.filter(Producto.Id == producto_id)
    
    resultados = query.all()
    
    resumen = []
    for r in resultados:
        estado = "Normal"
        if r.stock_actual <= 0:
            estado = "Sin stock"
        elif r.stock_actual <= r.stock_minimo:
            estado = "Bajo stock"
        
        resumen.append({
            "producto_id": r.Id,
            "producto_nombre": r.nombre,
            "producto_codigo": r.codigo,
            "stock_actual": r.stock_actual,
            "stock_minimo": r.stock_minimo,
            "total_entradas": r.total_entradas,
            "total_salidas": r.total_salidas,
            "ultimo_movimiento": r.ultimo_movimiento,
            "estado": estado
        })
    
    return resumen


def get_movimientos_por_dia(db: Session, dias: int = 30) -> List[Dict]:
    """Obtener movimientos agrupados por día"""
    fecha_limite = datetime.now() - timedelta(days=dias)
    
    resultados = db.query(
        func.date(Inventario.fecha_registro).label('fecha'),
        func.sum(func.case(
            (Inventario.tipo_movimiento.in_([TipoMovimiento.ENTRADA, TipoMovimiento.COMPRA]), 
             Inventario.cantidad),
            else_=0
        )).label('entradas'),
        func.sum(func.case(
            (Inventario.tipo_movimiento.in_([TipoMovimiento.SALIDA, TipoMovimiento.VENTA]), 
             Inventario.cantidad),
            else_=0
        )).label('salidas'),
        func.count(Inventario.Id).label('total_movimientos')
    ).filter(
        Inventario.fecha_registro >= fecha_limite,
        Inventario.estado == True
    ).group_by(
        func.date(Inventario.fecha_registro)
    ).order_by(
        func.date(Inventario.fecha_registro).desc()
    ).all()
    
    return [
        {
            "fecha": str(r.fecha),
            "entradas": r.entradas,
            "salidas": r.salidas,
            "total_movimientos": r.total_movimientos
        }
        for r in resultados
    ]


from datetime import timedelta