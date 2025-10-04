from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.auth.auth_handler import create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# In-memory user store for testing only
_fake_users = {}

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_active: Optional[bool] = True

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=201)
def register(data: RegisterRequest):
    if data.username in _fake_users:
        raise HTTPException(status_code=400, detail="User already exists")
    _fake_users[data.username] = {
        "username": data.username,
        "email": data.email,
        "password": data.password,
        "is_active": data.is_active,
    }
    return {"msg": "User registered"}

@router.post("/login")
def login(data: LoginRequest):
    user = _fake_users.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}
