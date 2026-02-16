""" Este archivo permite conectar con la base de datos """
from sqlalchemy import create_engine
import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker  


def create_db_if_no_exist():
    # Conexión al servidor (sin base de datos)
    connection = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        port=3307
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS autolavado")
    finally:
        connection.close()

create_db_if_no_exist()

# URL para SQLAlchemy (Aquí sí va la URL completa)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:1234@127.0.0.1:3307/autolavado"
  # Corregido: un solo ":" en el puerto
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
