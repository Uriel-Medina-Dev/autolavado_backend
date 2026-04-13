"""Esta clase representa la tabla rols de usuario."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.db import Base


class Rols(Base):
    """En este apartado se define la clase con sus atributos."""

    __tablename__ = "tbc_rols"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    status = Column(Boolean, default=True)
    creation_date = Column(DateTime, server_default=func.now(), nullable=False)
    update_date = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    usuarios = relationship("User", back_populates="rol")
    
    def __repr__(self):
        return f"<Rols(id={self.id}, name='{self.name}')>"