# app/cache/metrics.py
import time
from .redis_config import cache_manager

class CacheMetrics:

    @staticmethod
    def _get_time_bucket() -> int:
        """Retorna el bucket de 5 minutos para agrupar métricas"""
        return int(time.time() // 300)

    @staticmethod
    def track_cache_hit(key: str):
        """Registra un hit de cache"""
        bucket = CacheMetrics._get_time_bucket()
        metric_key = f"metrics:cache_hits:{bucket}"
        cache_manager.redis_client.incr(metric_key)
        cache_manager.redis_client.expire(metric_key, 3600)  # expira en 1h

    @staticmethod
    def track_cache_miss(key: str):
        """Registra un miss de cache"""
        bucket = CacheMetrics._get_time_bucket()
        metric_key = f"metrics:cache_misses:{bucket}"
        cache_manager.redis_client.incr(metric_key)
        cache_manager.redis_client.expire(metric_key, 3600)

    @staticmethod
    def get_cache_stats():
        """Obtiene estadísticas básicas de Redis"""
        info = cache_manager.redis_client.info()
        return {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }

    @staticmethod
    def get_custom_metrics():
        """Obtiene los contadores de hits/misses agrupados por buckets"""
        bucket = CacheMetrics._get_time_bucket()
        hits = cache_manager.redis_client.get(f"metrics:cache_hits:{bucket}") or 0
        misses = cache_manager.redis_client.get(f"metrics:cache_misses:{bucket}") or 0

        return {
            "time_bucket": bucket,
            "hits": int(hits),
            "misses": int(misses),
        }
