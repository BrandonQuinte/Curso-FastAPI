from sqlalchemy import Column, Integer, String
from database import Base


class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    cliente = Column(String, nullable=False)
    descripcion = Column(String)
    fecha_inicio = Column(String)  
    fecha_entrega = Column(String)
    estado = Column(String, default="pendiente")

# Clase básica User para autenticación
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
