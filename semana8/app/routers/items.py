from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from ..docs.descriptions import (
    ENDPOINT_DESCRIPTIONS,
    RESPONSE_DESCRIPTIONS,
    RESPONSE_EXAMPLES,
)
from ..models.schemas import (
    ErrorResponse,
    ListaUsuariosResponse,
    RolEnum,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
    responses={
        404: {
            "model": ErrorResponse,
            "description": RESPONSE_DESCRIPTIONS[404],
            "content": {
                "application/json": {
                    "examples": {
                        "no_encontrado": RESPONSE_EXAMPLES["error_no_encontrado"]
                    }
                }
            },
        },
        422: {
            "model": ErrorResponse,
            "description": RESPONSE_DESCRIPTIONS[422],
            "content": {
                "application/json": {
                    "examples": {"validacion": RESPONSE_EXAMPLES["error_validacion"]}
                }
            },
        },
    },
)

# Simulación de base de datos
usuarios_db = []
contador_id = 1


@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=201,
    summary="Crear nuevo usuario (Tipo D)",
    description=ENDPOINT_DESCRIPTIONS["crear_usuario"],
    responses={
        201: {
            "model": UsuarioResponse,
            "description": RESPONSE_DESCRIPTIONS[201],
            "content": {
                "application/json": {
                    "examples": {"creado": RESPONSE_EXAMPLES["usuario_creado"]}
                }
            },
        }
    },
)
async def crear_usuario(usuario: UsuarioCreate):
    """Crear un nuevo usuario en el sistema."""
    global contador_id

    # Validar unicidad del username
    if any(u["username"] == usuario.username for u in usuarios_db):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "USERNAME_DUPLICADO",
                "mensaje": f"El usuario '{usuario.username}' ya existe.",
                "codigo_http": 400,
                "timestamp": datetime.now(),
            },
        )

    nuevo_usuario = {
        "id": contador_id,
        **usuario.model_dump(),
        "activo": True,
        "fecha_creacion": datetime.now(),
        "ultima_conexion": None,
    }

    usuarios_db.append(nuevo_usuario)
    contador_id += 1

    return UsuarioResponse(**nuevo_usuario)


@router.get(
    "/",
    response_model=ListaUsuariosResponse,
    summary="Listar usuarios con filtros y paginación",
    description=ENDPOINT_DESCRIPTIONS["listar_usuarios"],
)
async def listar_usuarios(
    pagina: int = Query(1, ge=1, description="Número de página", example=1),
    limite: int = Query(
        10, ge=1, le=50, description="Usuarios por página (máx. 50)", example=10
    ),
    rol: Optional[RolEnum] = Query(
        None, description="Filtrar por rol de usuario", example="editor"
    ),
    activo: Optional[bool] = Query(
        None, description="Filtrar por estado activo/inactivo", example=True
    ),
    buscar: Optional[str] = Query(
        None, description="Buscar por username o email", example="admin"
    ),
    orden_por: str = Query("fecha_creacion", regex="^(username|fecha_creacion|rol)$"),
    direccion: str = Query("desc", regex="^(asc|desc)$"),
):
    """Listar usuarios del sistema con filtros y ordenamiento."""
    filtrados = usuarios_db.copy()

    if rol:
        filtrados = [u for u in filtrados if u["rol"] == rol]
    if activo is not None:
        filtrados = [u for u in filtrados if u["activo"] == activo]
    if buscar:
        b = buscar.lower()
        filtrados = [
            u
            for u in filtrados
            if b in u["username"].lower() or b in u["email"].lower()
        ]

    reverse = direccion == "desc"
    filtrados.sort(key=lambda x: x[orden_por], reverse=reverse)

    total = len(filtrados)
    inicio = (pagina - 1) * limite
    fin = inicio + limite
    pagina_usuarios = filtrados[inicio:fin]

    return ListaUsuariosResponse(
        usuarios=[UsuarioResponse(**u) for u in pagina_usuarios],
        total=total,
        pagina=pagina,
        por_pagina=limite,
    )


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obtener usuario por ID",
    description=ENDPOINT_DESCRIPTIONS["obtener_usuario"],
)
async def obtener_usuario(usuario_id: int = Path(..., gt=0, example=1)):
    """Obtener un usuario específico."""
    usuario = next((u for u in usuarios_db if u["id"] == usuario_id), None)
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "USUARIO_NO_ENCONTRADO",
                "mensaje": f"El usuario con ID {usuario_id} no fue encontrado",
                "codigo_http": 404,
                "timestamp": datetime.now(),
            },
        )
    return UsuarioResponse(**usuario)


@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Actualizar usuario existente",
    description=ENDPOINT_DESCRIPTIONS["actualizar_usuario"],
)
async def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate):
    """Actualizar parcialmente un usuario."""
    idx = next((i for i, u in enumerate(usuarios_db) if u["id"] == usuario_id), None)
    if idx is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "USUARIO_NO_ENCONTRADO",
                "mensaje": f"El usuario con ID {usuario_id} no fue encontrado",
                "codigo_http": 404,
                "timestamp": datetime.now(),
            },
        )

    update_data = datos.model_dump(exclude_unset=True)
    usuarios_db[idx].update(update_data)
    usuarios_db[idx]["ultima_conexion"] = datetime.now()

    return UsuarioResponse(**usuarios_db[idx])


@router.delete(
    "/{usuario_id}",
    status_code=204,
    summary="Eliminar usuario",
    description=ENDPOINT_DESCRIPTIONS["eliminar_usuario"],
)
async def eliminar_usuario(usuario_id: int):
    """Eliminar un usuario permanentemente."""
    idx = next((i for i, u in enumerate(usuarios_db) if u["id"] == usuario_id), None)
    if idx is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "USUARIO_NO_ENCONTRADO",
                "mensaje": f"El usuario con ID {usuario_id} no fue encontrado",
                "codigo_http": 404,
                "timestamp": datetime.now(),
            },
        )
    usuarios_db.pop(idx)
    return JSONResponse(status_code=204, content=None)


@router.get(
    "/estadisticas/resumen",
    tags=["reportes"],
    summary="Obtener estadísticas generales de usuarios",
    description="Obtiene un resumen estadístico de los usuarios del sistema Tipo D",
)
async def obtener_estadisticas_usuarios():
    """Estadísticas generales del catálogo de usuarios."""
    if not usuarios_db:
        return {
            "total_usuarios": 0,
            "activos": 0,
            "inactivos": 0,
            "por_roles": {},
        }

    activos = sum(1 for u in usuarios_db if u["activo"])
    roles = {}
    for u in usuarios_db:
        rol = u["rol"]
        roles[rol] = roles.get(rol, 0) + 1

    return {
        "total_usuarios": len(usuarios_db),
        "activos": activos,
        "inactivos": len(usuarios_db) - activos,
        "por_roles": roles,
    }
