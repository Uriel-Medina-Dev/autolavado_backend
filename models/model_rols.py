''' Esta clase representa la tabla rols de usuario '''
from sqlalchemy import Column, Integer, String, Boolean
from config.db import Base

class Rols(Base):
    ''' En este apartado se define la clase con sus atributos '''
    __tablename__ = "tbc_rol"
    
    Id = Column(Integer, primary_key = True, index = True)
    description = Column(String(60))
    status = Column(Boolean)
    creation_date = Column
    modification_date = Column()
