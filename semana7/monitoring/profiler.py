# monitoring/profiler.py
import cProfile
import pstats
import io
from memory_profiler import profile
from functools import wraps
import asyncio
import time
from typing import Dict, Any


class APIProfiler:
    def __init__(self, domain: str = "lang"):
        self.domain = domain
        self.profiles: Dict[str, Any] = {}
        self.memory_profiles: Dict[str, Any] = {}

    def profile_function(self, func_name: str = None):
        """
        Decorador para profiling de funciones/queries.
        Registra tiempo de ejecución y top de funciones más costosas.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                func_id = f"{self.domain}_{func_name or func.__name__}"

                # Profile CPU
                pr = cProfile.Profile()
                pr.enable()

                start_time = time.time()

                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                execution_time = time.time() - start_time
                pr.disable()

                # Guardar profiling
                s = io.StringIO()
                ps = pstats.Stats(pr, stream=s)
                ps.sort_stats("cumulative")
                ps.print_stats(20)  # Top 20 funciones más costosas

                self.profiles[func_id] = {
                    "execution_time": round(execution_time, 4),
                    "profile_data": s.getvalue(),
                    "timestamp": time.time()
                }

                return result
            return wrapper
        return decorator

    def get_profile_report(self, func_name: str = None) -> Dict[str, Any]:
        """
        Obtiene reporte de profiling (todo o por función específica).
        """
        if func_name:
            func_id = f"{self.domain}_{func_name}"
            return self.profiles.get(func_id, {})
        return self.profiles

    def clear_profiles(self):
        """Limpia los perfiles almacenados"""
        self.profiles.clear()
        self.memory_profiles.clear()


# Decorador específico para medir memoria en async
def memory_profile_async(profiler: APIProfiler):
    """
    Decorador para analizar consumo de memoria en endpoints críticos.
    Ejemplo: creación de cursos, asignación de niveles y grupos.
    """
    def decorator(func):
        @wraps(func)
        @profile  # memory_profiler
        async def wrapper(*args, **kwargs):
            func_id = f"{profiler.domain}_{func.__name__}"
            result = await func(*args, **kwargs)

            # Guardar referencia del análisis de memoria
            profiler.memory_profiles[func_id] = {
                "timestamp": time.time(),
                "note": "Perfil de memoria guardado para análisis"
            }
            return result
        return wrapper
    return decorator
