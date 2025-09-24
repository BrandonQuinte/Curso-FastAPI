# monitoring/metrics.py
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
import psutil
import time
from functools import wraps

class APIMetrics:
    def __init__(self, app_name: str, domain: str = "lang"):
        self.app_name = app_name
        self.domain = domain

        # Requests generales
        self.request_counter = Counter(
            f'{domain}_requests_total',
            'Total de requests por endpoint',
            ['method', 'endpoint', 'status']
        )

        self.response_time = Histogram(
            f'{domain}_response_duration_seconds',
            'Tiempo de respuesta por endpoint',
            ['method', 'endpoint'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )

        self.active_connections = Gauge(
            f'{domain}_active_connections',
            'Conexiones activas'
        )

        # Métricas del sistema
        self.system_metrics = {
            'cpu_usage': Gauge(f'{domain}_cpu_usage_percent', 'Uso de CPU'),
            'memory_usage': Gauge(f'{domain}_memory_usage_bytes', 'Uso de memoria'),
            'disk_usage': Gauge(f'{domain}_disk_usage_percent', 'Uso de disco')
        }

        # Métricas de negocio específicas del dominio Academia Idiomas
        self.business_metrics = self._create_business_metrics()

    def _create_business_metrics(self):
        """Crea métricas específicas para Academia Idiomas"""
        return {
            'cursos_creados': Counter(
                f'{self.domain}_cursos_creados_total',
                'Total de cursos creados'
            ),
            'niveles_creados': Counter(
                f'{self.domain}_niveles_creados_total',
                'Total de niveles creados en cursos'
            ),
            'grupos_creados': Counter(
                f'{self.domain}_grupos_creados_total',
                'Total de grupos creados en cursos'
            ),
            'cursos_actualizados': Counter(
                f'{self.domain}_cursos_actualizados_total',
                'Total de cursos actualizados'
            ),
            'api_errors': Counter(
                f'{self.domain}_api_errors_total',
                'Total de errores de API',
                ['error_type']
            )
        }

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Registra métricas de request"""
        self.request_counter.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()

        self.response_time.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    def update_system_metrics(self):
        """Actualiza métricas del sistema"""
        self.system_metrics['cpu_usage'].set(psutil.cpu_percent())
        self.system_metrics['memory_usage'].set(psutil.virtual_memory().used)
        self.system_metrics['disk_usage'].set(psutil.disk_usage('/').percent)

    def record_business_event(self, event_type: str, **kwargs):
        """Registra eventos de negocio (cursos, niveles, grupos, errores)"""
        if event_type in self.business_metrics:
            if hasattr(self.business_metrics[event_type], 'labels'):
                self.business_metrics[event_type].labels(**kwargs).inc()
            else:
                self.business_metrics[event_type].inc()

# Decorador para medir performance de endpoints
def monitor_performance(metrics: APIMetrics, method: str = "GET"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                metrics.record_request(
                    method=method,
                    endpoint=func.__name__,
                    status=200,
                    duration=duration
                )
                return result
            except Exception as e:
                duration = time.time() - start_time

                metrics.record_request(
                    method=method,
                    endpoint=func.__name__,
                    status=500,
                    duration=duration
                )

                metrics.record_business_event(
                    'api_errors',
                    error_type=type(e).__name__
                )
                raise
        return wrapper
    return decorator
