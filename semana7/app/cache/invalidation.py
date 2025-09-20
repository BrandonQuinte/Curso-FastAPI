# app/cache/invalidation.py
from fastapi import APIRouter
from .redis_config import cache_manager

router = APIRouter(prefix="/invalidate", tags=["Cache Invalidation"])

class AcademiaCacheInvalidation:

    @staticmethod
    async def on_curso_update(curso_id: str):
        """Invalida el cache relacionado a un curso específico"""
        patterns = [
            f"*curso*{curso_id}*",
            f"*catalogo_cursos*",
            f"*grupos_frecuentes*"
        ]
        for pattern in patterns:
            cache_manager.invalidate_cache(pattern)

    @staticmethod
    async def on_catalogo_update():
        """Invalida cache del catálogo completo"""
        cache_manager.invalidate_cache("*catalogo_cursos*")

    @staticmethod
    async def on_config_update():
        """Invalida configuraciones"""
        cache_manager.invalidate_cache("*config*")

# Endpoint de ejemplo para invalidar al actualizar curso
@router.put("/curso/{curso_id}")
async def update_curso(curso_id: str, data: dict):
    # Simula actualización en BD/dominio
    resultado = {"curso_id": curso_id, "actualizado": True, "data": data}

    # Invalida caches relacionados
    await AcademiaCacheInvalidation.on_curso_update(curso_id)

    return resultado
