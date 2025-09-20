# app/cache/redis_config.py
import redis
import json
from typing import Optional, Any
import os

class DomainCacheConfig:
    def __init__(self, domain_prefix: str):
        self.domain_prefix = domain_prefix  # Prefijo específico para el dominio
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=os.getenv('REDIS_PORT', 6379),
            db=0,
            decode_responses=True
        )

        # TTL específicos por tipo de dato en el dominio
        self.cache_ttl = {
            'frequent_data': 300,     # 5 minutos para datos frecuentes
            'stable_data': 3600,      # 1 hora para datos estables
            'reference_data': 86400,  # 24 horas para datos de referencia
            'temp_data': 60           # 1 minuto para datos temporales
        }

    def get_cache_key(self, category: str, identifier: str) -> str:
        """Genera claves de cache específicas para tu dominio"""
        return f"{self.domain_prefix}:{category}:{identifier}"

    def set_cache(self, key: str, value: Any, ttl_type: str = 'frequent_data') -> bool:
        """Almacena datos en cache con TTL específico"""
        try:
            cache_key = self.get_cache_key("data", key)
            serialized_value = json.dumps(value)
            ttl = self.cache_ttl.get(ttl_type, 300)
            return self.redis_client.setex(cache_key, ttl, serialized_value)
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        """Recupera datos del cache"""
        try:
            cache_key = self.get_cache_key("data", key)
            cached_value = self.redis_client.get(cache_key)
            if cached_value:
                return json.loads(cached_value)
            return None
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None

    def invalidate_cache(self, pattern: str = None):
        """Invalida cache específico o por patrón"""
        try:
            if pattern:
                cache_pattern = self.get_cache_key("data", pattern)
                keys = self.redis_client.keys(cache_pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # Invalida todo el cache de tu dominio
                domain_keys = self.redis_client.keys(f"{self.domain_prefix}:*")
                if domain_keys:
                    self.redis_client.delete(*domain_keys)
        except Exception as e:
            print(f"Error invalidating cache: {e}")

# Instancia específica para "Academia Idiomas"
# Reemplaza "lang_" como prefijo, con el enfoque en niveles y grupos de curso
cache_manager = DomainCacheConfig("lang_")
