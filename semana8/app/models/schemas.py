from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NivelAccesoEnum(str, Enum):
    """Niveles de acceso para usuarios tipo D"""

    ADMIN = "admin"
    EDITOR = "editor"
    LECTOR = "lector"


class UsuarioTipoDBase(BaseModel):
    """Esquema base para usuarios tipo D (gestión de catálogo de usuarios/roles)"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "usuario_demo",
                "email": "demo@correo.com",
                "rol": "editor",
                "activo": True,
            }
        }
    )

    username: str = Field(
        ...,
        description="Nombre de usuario único",
        min_length=3,
        max_length=50,
        examples=["usuario1", "admin123"],
    )

    email: str = Field(
        ...,
        description="Correo electrónico del usuario",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        examples=["usuario@dominio.com"],
    )

    rol: NivelAccesoEnum = Field(
        ...,
        description="Nivel de acceso o rol del usuario",
        examples=["admin", "editor", "lector"],
    )

    activo: bool = Field(
        True,
        description="Indica si el usuario está activo en el sistema",
        examples=[True, False],
    )


class UsuarioTipoDCreate(UsuarioTipoDBase):
    """Esquema para creación de usuarios tipo D"""

    password: str = Field(
        ...,
        min_length=6,
        description="Contraseña del usuario",
        examples=["password_segura_123"],
    )


class UsuarioTipoDUpdate(BaseModel):
    """Esquema para actualizar usuarios tipo D"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "nuevo@correo.com", "rol": "admin", "activo": False}
        }
    )

    email: Optional[str] = Field(None, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    rol: Optional[NivelAccesoEnum] = None
    activo: Optional[bool] = None


class UsuarioTipoDResponse(UsuarioTipoDBase):
    """Esquema de respuesta para usuarios tipo D"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 10,
                "username": "usuario_demo",
                "email": "demo@correo.com",
                "rol": "editor",
                "activo": True,
                "fecha_creacion": "2024-03-15T09:00:00",
                "ultima_conexion": "2024-03-16T12:30:00",
            }
        }
    )

    id: int = Field(..., description="Identificador único del usuario")
    fecha_creacion: datetime = Field(..., description="Fecha de creación del usuario")
    ultima_conexion: Optional[datetime] = Field(
        None, description="Última conexión registrada"
    )


class ListaUsuariosDResponse(BaseModel):
    """Respuesta paginada para usuarios tipo D"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "usuarios": [
                    {
                        "id": 1,
                        "username": "admin_user",
                        "email": "admin@correo.com",
                        "rol": "admin",
                        "activo": True,
                    }
                ],
                "total": 1,
                "pagina": 1,
                "por_pagina": 10,
            }
        }
    )

    usuarios: List[UsuarioTipoDResponse]
    total: int
    pagina: int
    por_pagina: int
