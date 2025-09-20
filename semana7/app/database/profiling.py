# app/database/profiling.py
import time
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Configurar logging para consultas lentas
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sql_performance")

# Lista global de consultas lentas detectadas
slow_queries = []

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Marca el tiempo de inicio de la consulta."""
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Calcula duración y registra si la consulta es lenta."""
    total = time.time() - context._query_start_time
    if total > 0.1:  # Log consultas que toman más de 100ms
        query_info = {
            "duration": total,
            "statement": statement,
            "parameters": parameters,
        }
        slow_queries.append(query_info)
        logger.warning(f"Consulta lenta ({total:.3f}s): {statement[:100]}...")

# Función para analizar consultas específicas del dominio Academia Idiomas
def analyze_domain_queries(domain_prefix: str = "lang_"):
    """
    Analiza las consultas lentas relacionadas con el dominio Academia Idiomas.
    Filtra por entidad principal 'curso', niveles o grupos de cursos.
    """
    domain_slow_queries = []
    focus_keywords = ["curso", "nivel", "grupo"]

    for q in slow_queries:
        if domain_prefix in q["statement"].lower():
            # Si la consulta toca cursos, niveles o grupos → la marcamos
            if any(keyword in q["statement"].lower() for keyword in focus_keywords):
                domain_slow_queries.append(q)

    return domain_slow_queries
