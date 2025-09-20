# app/middleware/domain_rate_limiter.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis
import time
from typing import Dict

class DomainRateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, domain_prefix: str, redis_client: redis.Redis):
        super().__init__(app)
        self.domain_prefix = domain_prefix
        self.redis = redis_client

        # Configuración específica por dominio
        self.rate_limits = self._get_domain_rate_limits(domain_prefix)

    def _get_domain_rate_limits(self, domain_prefix: str) -> Dict[str, Dict]:
        """Configuración de límites específicos por dominio"""

        rate_configs = {
            "lang_": {
                # Academia Idiomas: más tráfico en niveles y grupos
                "courses": {"requests": 120, "window": 60},    # 120 req/min cursos
                "levels": {"requests": 200, "window": 60},     # 200 req/min niveles
                "groups": {"requests": 180, "window": 60},     # 180 req/min grupos
                "general": {"requests": 150, "window": 60},    # general
                "admin": {"requests": 50, "window": 60}        # admin
            },
            "vet_": { ... },   # tu config original
            "edu_": { ... },   # tu config original
            "gym_": { ... },   # tu config original
            "pharma_": { ... } # tu config original
        }

        default_config = {
            "high_priority": {"requests": 200, "window": 60},
            "medium_priority": {"requests": 100, "window": 60},
            "low_priority": {"requests": 50, "window": 60},
            "general": {"requests": 120, "window": 60},
            "admin": {"requests": 30, "window": 60}
        }

        return rate_configs.get(domain_prefix, default_config)

    def _get_rate_limit_category(self, path: str, method: str) -> str:
        """Determina la categoría de rate limit según el endpoint"""

        if self.domain_prefix == "lang_":
            if "/cursos" in path:
                return "courses"
            elif "/niveles" in path:
                return "levels"
            elif "/grupos" in path:
                return "groups"
            elif "/admin" in path:
                return "admin"

        # Reutiliza tus otras configuraciones (vet_, edu_, gym_, pharma_) aquí
        # ...

        return "general"

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path
        method = request.method

        # Solo aplica a este dominio
        if not path.startswith(f"/{self.domain_prefix.rstrip('_')}"):
            return await call_next(request)

        category = self._get_rate_limit_category(path, method)
        rate_config = self.rate_limits.get(category, self.rate_limits["general"])

        if not self._check_rate_limit(client_ip, category, rate_config):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "category": category,
                    "limit": rate_config["requests"],
                    "window": rate_config["window"],
                    "domain": self.domain_prefix
                }
            )

        return await call_next(request)

    def _check_rate_limit(self, client_ip: str, category: str, config: Dict) -> bool:
        current_time = int(time.time())
        window_start = current_time - config["window"]

        key = f"{self.domain_prefix}:rate_limit:{category}:{client_ip}"

        requests = self.redis.zrangebyscore(key, window_start, current_time)
        if len(requests) >= config["requests"]:
            return False

        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, config["window"])
        self.redis.zremrangebyscore(key, 0, window_start)

        return True
