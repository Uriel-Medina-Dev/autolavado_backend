"""Esta clase representa la tabla rols de usuario."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from config.db import Base  # Ahora debería funcionar


class Rols(Base):
    """En este apartado se define la clase con sus atributos."""

    __tablename__ = "tbc_rols"
    
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    status = Column(Boolean)
    creation_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, onupdate=func.now())
    
    # Para evitar la advertencia de "too-few-public-methods"
    def __repr__(self):
        return f"<Rols(id={self.id}, name='{self.name}')>"