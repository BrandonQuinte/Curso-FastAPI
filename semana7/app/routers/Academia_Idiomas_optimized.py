# app/routers/academia_idiomas_optimized.py
from fastapi import APIRouter, HTTPException
from ..cache.cache_decorators import cache_result
from typing import List, Dict

router = APIRouter(prefix="/lang", tags=["Academia Idiomas Optimizada"])

# Simulando un servicio que interactúa con la base de datos o fuente de datos
class ServicioDominio:
    @staticmethod
    async def get_grupos_frecuentes() -> List[Dict]:
        return [
            {"id": 1, "nombre": "Inglés A1", "descripcion": "Curso para principiantes de inglés"},
            {"id": 2, "nombre": "Inglés A2", "descripcion": "Curso para nivel intermedio bajo"},
            {"id": 3, "nombre": "Inglés B1", "descripcion": "Curso para nivel intermedio alto"},
        ]

    @staticmethod
    async def get_niveles() -> List[str]:
        return ["A1", "A2", "B1", "B2", "C1", "C2"]

    @staticmethod
    async def get_catalogo_cursos() -> List[Dict]:
        return [
            {"id": 1, "curso": "Inglés A1", "duracion": "3 meses", "descripcion": "Curso de inglés para principiantes"},
            {"id": 2, "curso": "Inglés A2", "duracion": "3 meses", "descripcion": "Curso de inglés para nivel básico"},
            {"id": 3, "curso": "Inglés B1", "duracion": "3 meses", "descripcion": "Curso de inglés para nivel intermedio"},
        ]

# Instancia del servicio
tu_servicio_dominio = ServicioDominio()

@router.get("/grupos/frecuentes")
@cache_result(ttl_type='frequent_data', key_prefix='grupos_frecuentes')
async def get_grupos_frecuentes():
    try:
        return await tu_servicio_dominio.get_grupos_frecuentes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener grupos de cursos: {str(e)}")

@router.get("/niveles")
@cache_result(ttl_type='stable_data', key_prefix='niveles')
async def get_niveles_curso():
    try:
        return await tu_servicio_dominio.get_niveles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener niveles de curso: {str(e)}")

@router.get("/catalogo")
@cache_result(ttl_type='reference_data', key_prefix='catalogo_cursos')
async def get_catalogo_cursos():
    try:
        return await tu_servicio_dominio.get_catalogo_cursos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener catálogo de cursos: {str(e)}")
