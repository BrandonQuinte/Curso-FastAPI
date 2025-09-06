# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Literal

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str  # NUEVO: incluir role en respuesta

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# NUEVO: Schema para actualizar roles (solo admin)
class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin"]