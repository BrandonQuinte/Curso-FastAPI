# app/database/performance_monitor.py
import time
from sqlalchemy import text
from sqlalchemy.orm import Session
from contextlib import contextmanager

class DatabasePerformanceMonitor:

    @staticmethod
    @contextmanager
    def measure_query_time(query_name: str):
        """Context manager para medir tiempo de consultas"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            print(f"⏱ Query '{query_name}' ejecutada en {duration:.3f}s")

            # Log si es lenta (ajusta el threshold a tu contexto)
            if duration > 0.5:  # 500ms
                print(f"⚠️  Consulta lenta detectada: {query_name}")

    @staticmethod
    def get_database_stats(db: Session):
        """Obtiene estadísticas generales de la base de datos"""
        stats_query = """
        SELECT
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation
        FROM pg_stats
        WHERE schemaname = 'public'
          AND tablename IN ('cursos', 'niveles', 'grupos', 'inscripciones', 'profesores')
        ORDER BY tablename, attname;
        """
        result = db.execute(text(stats_query))
        return [dict(row) for row in result]

    @staticmethod
    def analyze_slow_queries(db: Session, domain_prefix: str = "lang_"):
        """
        Analiza consultas lentas específicas del dominio.
        Requiere que la extensión `pg_stat_statements` esté habilitada en Postgres.
        """
        slow_queries = f"""
        SELECT query, calls, total_time, mean_time
        FROM pg_stat_statements
        WHERE query ILIKE '%%{domain_prefix}%%'
           OR query ILIKE '%%cursos%%'
           OR query ILIKE '%%niveles%%'
           OR query ILIKE '%%grupos%%'
        ORDER BY mean_time DESC
        LIMIT 10;
        """
        try:
            result = db.execute(text(slow_queries))
            return [dict(row) for row in result]
        except Exception as e:
            print(f"Error analizando consultas lentas: {e}")
            return []
