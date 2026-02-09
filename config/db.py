""" Este archivo permite conectar con la base de datos """
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker  

SQLALCHEMY_DATABASE_URL = "mysql://root:1234@127.0.0.1:3308/autolavado"  # Corregido: un solo ":" en el puerto
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
