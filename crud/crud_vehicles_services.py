"""CRUD para vehículos servicios - operaciones básicas y consultas complejas"""
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, extract
from models.model_vehicles_services import VehiculoServicio
from models.model_vehicle import Vehicle
from models.model_user import User
from models.model_service import Servicios
from schemas.schema_vehicles_services import UsuariosVehiculoServicioCreate, UsuariosVehiculoServicioUpdate
from datetime import datetime, date
from typing import List, Optional, Dict


# ============= OPERACIONES BÁSICAS CRUD =============

def get_vehicles_services(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todas las asignaciones"""
    return db.query(VehiculoServicio).offset(skip).limit(limit).all()


def get_vehicle_service_by_id(db: Session, vs_id: int):
    """Obtener una asignación por ID"""
    return db.query(VehiculoServicio).filter(VehiculoServicio.Id == vs_id).first()


def create_vehicle_service(db: Session, vs: UsuariosVehiculoServicioCreate):
    """Crear una nueva asignación"""
    db_vs = VehiculoServicio(
        vehicle_Id=vs.vehicle_Id,
        cajero_Id=vs.cajero_Id,
        operativo_Id=vs.operativo_Id,
        servicio_Id=vs.servicio_Id,
        date=vs.date,
        time=vs.time,
        estatus=vs.estatus,
        descuento=vs.descuento if hasattr(vs, 'descuento') else 0,
        estado=vs.estado,
        fecha_registro=datetime.now(),
        fecha_actualizacion=datetime.now()
    )
    db.add(db_vs)
    db.commit()
    db.refresh(db_vs)
    return db_vs


def update_vehicle_service(db: Session, vs_id: int, vs: UsuariosVehiculoServicioUpdate):
    """Actualizar una asignación existente"""
    db_vs = db.query(VehiculoServicio).filter(VehiculoServicio.Id == vs_id).first()
    if db_vs:
        update_data = vs.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vs, field, value)
        
        db_vs.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_vs)
    return db_vs


def delete_vehicle_service(db: Session, vs_id: int, hard_delete: bool = False):
    """Eliminar una asignación (lógica o físicamente)"""
    db_vs = db.query(VehiculoServicio).filter(VehiculoServicio.Id == vs_id).first()
    if db_vs:
        if hard_delete:
            db.delete(db_vs)
        else:
            db_vs.estado = False
            db_vs.fecha_actualizacion = datetime.now()
        db.commit()
    return db_vs


# ============= CONSULTAS COMPLEJAS CON JOINS =============

def get_asignaciones_completas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    estatus: Optional[str] = None,
    cajero_id: Optional[int] = None,
    vehiculo_id: Optional[int] = None
) -> List[Dict]:
    """
    Obtener asignaciones con toda la información mediante JOINs
    """
    # Crear alias para las diferentes relaciones de usuario
    Propietario = aliased(User, name="propietario")
    Cajero = aliased(User, name="cajero")
    Operativo = aliased(User, name="operativo")
    
    query = db.query(
        VehiculoServicio.Id.label("asignacion_id"),
        VehiculoServicio.date,
        VehiculoServicio.time,
        VehiculoServicio.estatus,
        VehiculoServicio.descuento,
        VehiculoServicio.fecha_registro,
        
        # Vehículo
        Vehicle.Id.label("vehiculo_id"),
        Vehicle.placa,
        Vehicle.modelo.label("vehiculo_modelo"),
        Vehicle.color.label("vehiculo_color"),
        Vehicle.tipo.label("vehiculo_tipo"),
        Vehicle.anio.label("vehiculo_anio"),
        
        # Propietario (dueño del vehículo)
        Propietario.Id.label("propietario_id"),
        Propietario.user_name.label("propietario_nombre"),
        Propietario.user_1lastname.label("propietario_apellido1"),
        Propietario.user_2lastname.label("propietario_apellido2"),
        Propietario.user_phone.label("propietario_telefono"),
        
        # Cajero
        Cajero.Id.label("cajero_id"),
        Cajero.user_name.label("cajero_nombre"),
        Cajero.user_1lastname.label("cajero_apellido1"),
        Cajero.user_2lastname.label("cajero_apellido2"),
        
        # Operativo
        Operativo.Id.label("operativo_id"),
        Operativo.user_name.label("operativo_nombre"),
        Operativo.user_1lastname.label("operativo_apellido1"),
        Operativo.user_2lastname.label("operativo_apellido2"),
        
        # Servicio
        Servicios.Id.label("servicio_id"),
        Servicios.nombre.label("servicio_nombre"),
        Servicios.descripcion.label("servicio_descripcion"),
        Servicios.costo.label("servicio_precio_original")
    ).join(
        Vehicle, VehiculoServicio.vehicle_Id == Vehicle.Id
    ).join(
        Propietario, Vehicle.usuario_Id == Propietario.Id  # Propietario
    ).join(
        Cajero, VehiculoServicio.cajero_Id == Cajero.Id  # Cajero
    ).join(
        Operativo, VehiculoServicio.operativo_Id == Operativo.Id  # Operativo
    ).join(
        Servicios, VehiculoServicio.servicio_Id == Servicios.Id
    ).filter(
        VehiculoServicio.estado == True
    )
    
    # Aplicar filtros
    if fecha_inicio:
        query = query.filter(VehiculoServicio.date >= fecha_inicio)
    if fecha_fin:
        query = query.filter(VehiculoServicio.date <= fecha_fin)
    if estatus:
        query = query.filter(VehiculoServicio.estatus == estatus)
    if cajero_id:
        query = query.filter(VehiculoServicio.cajero_Id == cajero_id)
    if vehiculo_id:
        query = query.filter(VehiculoServicio.vehicle_Id == vehiculo_id)
    
    # Ordenar por fecha descendente
    query = query.order_by(VehiculoServicio.date.desc(), VehiculoServicio.time.desc())
    
    # Paginación
    resultados = query.offset(skip).limit(limit).all()
    
    # Procesar resultados
    asignaciones = []
    for r in resultados:
        precio_original = float(r.servicio_precio_original) if r.servicio_precio_original else 0
        descuento = float(r.descuento) if r.descuento else 0
        precio_final = precio_original - (precio_original * descuento / 100) if descuento > 0 else precio_original
        
        asignacion = {
            "asignacion_id": r.asignacion_id,
            "fecha": str(r.date) if r.date else None,
            "hora": str(r.time) if r.time else None,
            "estatus": str(r.estatus.value) if hasattr(r.estatus, 'value') else str(r.estatus),
            "descuento": descuento,
            "fecha_registro": str(r.fecha_registro) if r.fecha_registro else None,
            
            # Vehículo
            "vehiculo_id": r.vehiculo_id,
            "placa": r.placa,
            "vehiculo_modelo": r.vehiculo_modelo,
            "vehiculo_color": r.vehiculo_color,
            "vehiculo_tipo": r.vehiculo_tipo,
            "vehiculo_anio": r.vehiculo_anio,
            
            # Propietario
            "propietario_id": r.propietario_id,
            "propietario_nombre": f"{r.propietario_nombre or ''} {r.propietario_apellido1 or ''} {r.propietario_apellido2 or ''}".strip(),
            "propietario_telefono": r.propietario_telefono,
            
            # Cajero
            "cajero_id": r.cajero_id,
            "cajero_nombre": f"{r.cajero_nombre or ''} {r.cajero_apellido1 or ''} {r.cajero_apellido2 or ''}".strip(),
            
            # Operativo
            "operativo_id": r.operativo_id,
            "operativo_nombre": f"{r.operativo_nombre or ''} {r.operativo_apellido1 or ''} {r.operativo_apellido2 or ''}".strip(),
            
            # Servicio
            "servicio_id": r.servicio_id,
            "servicio_nombre": r.servicio_nombre,
            "servicio_descripcion": r.servicio_descripcion,
            "servicio_precio_original": round(precio_original, 2),
            "precio_final": round(precio_final, 2)
        }
        asignaciones.append(asignacion)
    
    return asignaciones


def get_asignacion_completa_by_id(db: Session, asignacion_id: int) -> Optional[Dict]:
    """Obtener una asignación completa por ID"""
    resultados = get_asignaciones_completas(db, limit=1000)
    for r in resultados:
        if r["asignacion_id"] == asignacion_id:
            return r
    return None


def get_resumen_ventas(
    db: Session,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None
) -> Dict:
    """Obtener resumen de ventas para un período"""
    
    query = db.query(
        VehiculoServicio,
        Servicios.costo
    ).join(
        Servicios, VehiculoServicio.servicio_Id == Servicios.Id
    ).filter(
        VehiculoServicio.estado == True,
        VehiculoServicio.estatus.in_(["Realizada", "Proceso"])
    )
    
    if fecha_inicio:
        query = query.filter(VehiculoServicio.date >= fecha_inicio)
    if fecha_fin:
        query = query.filter(VehiculoServicio.date <= fecha_fin)
    
    resultados = query.all()
    
    total_asignaciones = len(resultados)
    total_ingresos = 0
    total_descuentos = 0
    
    servicio_count = {}
    cajero_count = {}
    
    for vs, costo in resultados:
        precio_original = float(costo) if costo else 0
        descuento = float(vs.descuento) if vs.descuento else 0
        precio_final = precio_original - (precio_original * descuento / 100) if descuento > 0 else precio_original
        
        total_ingresos += precio_final
        total_descuentos += (precio_original - precio_final)
        
        # Conteo de servicios
        if vs.servicio_Id in servicio_count:
            servicio_count[vs.servicio_Id] += 1
        else:
            servicio_count[vs.servicio_Id] = 1
        
        # Conteo de cajeros
        if vs.cajero_Id in cajero_count:
            cajero_count[vs.cajero_Id] += 1
        else:
            cajero_count[vs.cajero_Id] = 1
    
    # Servicio más solicitado
    servicio_mas_solicitado = None
    if servicio_count:
        servicio_id_top = max(servicio_count, key=servicio_count.get)
        servicio = db.query(Servicios).filter(Servicios.Id == servicio_id_top).first()
        servicio_mas_solicitado = servicio.nombre if servicio else None
    
    # Cajero destacado
    cajero_destacado = None
    if cajero_count:
        cajero_id_top = max(cajero_count, key=cajero_count.get)
        cajero = db.query(User).filter(User.Id == cajero_id_top).first()
        if cajero:
            cajero_destacado = f"{cajero.user_name} {cajero.user_1lastname}"
    
    promedio = total_ingresos / total_asignaciones if total_asignaciones > 0 else 0
    
    periodo = "todo el tiempo"
    if fecha_inicio and fecha_fin:
        periodo = f"{fecha_inicio} a {fecha_fin}"
    elif fecha_inicio:
        periodo = f"desde {fecha_inicio}"
    elif fecha_fin:
        periodo = f"hasta {fecha_fin}"
    
    return {
        "total_asignaciones": total_asignaciones,
        "total_ingresos": round(total_ingresos, 2),
        "total_descuentos": round(total_descuentos, 2),
        "promedio_por_servicio": round(promedio, 2),
        "servicio_mas_solicitado": servicio_mas_solicitado,
        "cajero_destacado": cajero_destacado,
        "periodo": periodo
    }


def get_ventas_por_dia(db: Session, mes: int, año: int) -> List[Dict]:
    """Obtener ventas agrupadas por día para un mes específico"""
    
    resultados = db.query(
        extract('day', VehiculoServicio.date).label('dia'),
        func.count(VehiculoServicio.Id).label('cantidad'),
        func.sum(Servicios.costo - (Servicios.costo * VehiculoServicio.descuento / 100)).label('total')
    ).join(
        Servicios, VehiculoServicio.servicio_Id == Servicios.Id
    ).filter(
        extract('month', VehiculoServicio.date) == mes,
        extract('year', VehiculoServicio.date) == año,
        VehiculoServicio.estatus.in_(["Realizada", "Proceso"]),
        VehiculoServicio.estado == True
    ).group_by(
        'dia'
    ).order_by(
        'dia'
    ).all()
    
    return [
        {
            "dia": int(r.dia) if r.dia else 0,
            "cantidad_servicios": int(r.cantidad) if r.cantidad else 0,
            "total_ventas": round(float(r.total), 2) if r.total else 0
        }
        for r in resultados
    ]


def get_estadisticas_cajero(
    db: Session,
    cajero_id: int,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None
) -> Dict:
    """Obtener estadísticas de ventas de un cajero específico"""
    asignaciones = get_asignaciones_completas(
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