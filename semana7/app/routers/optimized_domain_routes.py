# app/routers/optimized_domain_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.services.optimized_domain_service import OptimizedDomainService
from app.database.get_db import get_db

router = APIRouter(prefix="/lang/optimized", tags=["Optimized Domain - Academia Idiomas"])

@router.get("/cursos/nivel/{nivel}")
async def cursos_por_nivel(
    nivel: str,
    estado: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Cursos filtrados por nivel (A1, A2, B1, B2, C1, C2)"""
    service = OptimizedDomainService(db, "lang_")
    return await service.get_cursos_por_nivel(nivel, estado, limit, offset)

@router.get("/cursos/{curso_id}/inscripciones")
async def inscripciones_por_curso(
    curso_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Inscripciones activas de un curso específico"""
    service = OptimizedDomainService(db, "lang_")
    return await service.get_inscripciones_por_curso(curso_id, limit, offset)

@router.get("/cursos/{curso_id}/grupos")
async def grupos_por_curso(curso_id: int, db: Session = Depends(get_db)):
    """Grupos asignados a un curso específico"""
    service = OptimizedDomainService(db, "lang_")
    return await service.get_grupos_por_curso(curso_id)

@router.get("/cursos/proximos")
async def proximos_cursos(db: Session = Depends(get_db)):
    """Próximos cursos que inician en la Academia"""
    service = OptimizedDomainService(db, "lang_")
    return await service.get_proximos_cursos()

@router.get("/profesores/{profesor_id}/cursos")
async def cursos_por_profesor(profesor_id: int, db: Session = Depends(get_db)):
    """Cursos dictados por un profesor"""
    service = OptimizedDomainService(db, "lang_")
    return await service.get_cursos_por_profesor(profesor_id)
