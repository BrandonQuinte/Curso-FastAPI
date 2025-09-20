# tests/test_database_optimization.py
import pytest
import time
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.optimized_domain_service import OptimizedDomainService

class TestDatabaseOptimization:

    @pytest.mark.asyncio
    async def test_critical_query_performance(self, db_session: Session):
        """Verifica que las consultas críticas (ej. cursos/niveles) sean rápidas"""
        service = OptimizedDomainService(db_session, "lang_")

        start_time = time.time()
        result = await service.get_critical_data(1)
        duration = time.time() - start_time

        # Debe ejecutarse en menos de 200ms
        assert duration < 0.2, f"Consulta crítica muy lenta: {duration:.3f}s"
        assert result is not None

    @pytest.mark.asyncio
    async def test_availability_query_performance(self, db_session: Session):
        """Verifica performance de consultas de disponibilidad (grupos/niveles)"""
        service = OptimizedDomainService(db_session, "lang_")

        start_time = time.time()
        result = await service.get_availability_data()
        duration = time.time() - start_time

        # Debe ejecutarse en menos de 300ms
        assert duration < 0.3, f"Consulta de disponibilidad lenta: {duration:.3f}s"

    def test_indexes_exist(self, db_session: Session):
        """Verifica que los índices específicos de Academia Idiomas existan"""
        check_indexes = """
        SELECT indexname, tablename
        FROM pg_indexes
        WHERE tablename IN ('cursos', 'niveles', 'grupos', 'inscripciones')
          OR indexname LIKE 'lang_%';
        """

        result = db_session.execute(text(check_indexes))
        indexes = [dict(row) for row in result]

        # Debe haber al menos 2 índices específicos
        assert len(indexes) >= 2, "Faltan índices específicos del dominio"
