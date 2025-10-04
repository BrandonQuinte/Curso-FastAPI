"""
Módulo de autenticación JWT - Dominio Tipo D (Inmobiliaria Premium RealEstate)
Provee utilidades para generar y validar tokens de acceso.
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

# ============================================================
# ⚙️ Configuración del Token
# ============================================================

SECRET_KEY = "inmobiliaria_premium_secret_key_2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ============================================================
# 🧩 Generación de Tokens
# ============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT a partir de un diccionario con datos del usuario.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ============================================================
# 🔍 Verificación del Token
# ============================================================

def verify_access_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT. Lanza error si no es válido o está expirado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta 'sub'.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================
# 👤 Dependencia para rutas protegidas
# ============================================================

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependencia usada en rutas protegidas. Retorna la información del usuario autenticado.
    """
    return verify_access_token(token)
