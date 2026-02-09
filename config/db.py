''' Este archivo permite conectar con la base de datos '''
from SQLAlchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlachemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql://root:1234@127.0.0.1::3308/autolavado"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
