"""Esta clase representa la tabla de cajeros (información adicional)"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.db import Base


class Cajero(Base):
    """Modelo para cajeros - información adicional específica del puesto"""
    
    __tablename__ = "tbb_cajeros"
    
    Id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("tbb_user.Id"), unique=True, nullable=False)
    
    # Información laboral específica
    numero_empleado = Column(String(20), unique=True, nullable=False)
    turno = Column(String(20), nullable=False)  # Matutino, Vespertino, Nocturno
    numero_caja = Column(Integer, nullable=True)
    fecha_contratacion = Column(Date, nullable=False)
    salario = Column(Float, nullable=True)
    
    # Contacto de emergencia
    contacto_emergencia_nombre = Column(String(100), nullable=True)
    contacto_emergencia_telefono = Column(String(15), nullable=True)
    contacto_emergencia_parentesco = Column(String(30), nullable=True)
    
    # Datos bancarios
    banco = Column(String(50), nullable=True)
    cuenta_bancaria = Column(String(30), nullable=True)
    clabe = Column(String(20), nullable=True)
    
    # Campos de auditoría
    estado = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    usuario = relationship("User", back_populates="cajero_info")
    
    def __repr__(self):
        return f"<Cajero(id={self.Id}, empleado='{self.numero_empleado}')>"