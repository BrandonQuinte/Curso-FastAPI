# app/services/optimized_domain_service.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.optimized_queries import DomainOptimizedQueries
from typing import List, Dict, Any

class OptimizedDomainService:
    def __init__(self, db: Session, domain_prefix: str = "lang_"):
        self.db = db
        self.domain_prefix = domain_prefix
        self.queries = DomainOptimizedQueries.get_queries_for_domain(domain_prefix)

    async def execute_optimized_query(self, query_name: str, params: Dict[str, Any]) -> List[Dict]:
        """Ejecuta consulta optimizada específica del dominio"""
        if query_name not in self.queries:
            raise ValueError(f"Query {query_name} no encontrada para dominio {self.domain_prefix}")

        query = self.queries[query_name]
        result = self.db.execute(text(query), params)
        return [dict(row) for row in result]

    # 📌 Métodos específicos para Academia de Idiomas
    async def get_cursos_por_nivel(self, nivel: str, estado: str = None, limit: int = 10, offset: int = 0) -> List[Dict]:
        return await self.execute_optimized_query("cursos_por_nivel", {
            "nivel": nivel,
            "estado": estado,
            "limit": limit,
            "offset": offset
        })

    async def get_inscripciones_por_curso(self, curso_id: int, limit: int = 20, offset: int = 0) -> List[Dict]:
        return await self.execute_optimized_query("inscripciones_por_curso", {
            "curso_id": curso_id,
            "limit": limit,
            "offset": offset
        })

    async def get_grupos_por_curso(self, curso_id: int) -> List[Dict]:
        return await self.execute_optimized_query("grupos_por_curso", {
            "curso_id": curso_id
        })

    async def get_proximos_cursos(self) -> List[Dict]:
        return await self.execute_optimized_query("proximos_cursos", {})

    async def get_cursos_por_profesor(self, profesor_id: int) -> List[Dict]:
        return await self.execute_optimized_query("cursos_por_profesor", {
            "profesor_id": profesor_id
        })
