"""Configuración de la base de datos - Dominio Tipo D (Inmobiliaria Premium RealEstate)"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os




DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/realestate_db"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
    future=True
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()




def get_db():
    """
    Provee una sesión de base de datos para cada request.
    Se usa como dependencia en los endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




def init_db():
    """
    Inicializa las tablas en la base de datos.
    Ideal para ejecución manual o entornos de staging.
    """
    from app.models import all_models  # Carga todos los modelos al Base
    Base.metadata.create_all(bind=engine)
