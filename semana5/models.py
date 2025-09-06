# models.py
from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)  # Guardamos el hash, NO el password
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")  # NUEVO: campo role

    


