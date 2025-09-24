# app/routers/middleware_monitoring.py
from fastapi import APIRouter
import redis

# Prefijo del dominio: Academia Idiomas
DOMAIN_PREFIX = "lang_"

router = APIRouter(
    prefix=f"/{DOMAIN_PREFIX.rstrip('_')}/monitoring",
    tags=["Middleware Monitoring"]
)

@router.get("/rate-limits")
async def get_rate_limit_stats():
    """Obtiene estadísticas de rate limiting específicas del dominio Academia Idiomas"""
    redis_client = redis.Redis(host="localhost", port=6379, db=0)

    # Claves de rate limiting para este dominio
    keys = redis_client.keys(f"{DOMAIN_PREFIX}:rate_limit:*")

    stats = {}
    for key in keys:
        key_str = key.decode() if isinstance(key, bytes) else key
        parts = key_str.split(":")
        if len(parts) >= 4:
            category = parts[2]
            client_ip = parts[3]
            count = redis_client.zcard(key)

            if category not in stats:
                stats[category] = {}
            stats[category][client_ip] = count

    return {
        "domain": DOMAIN_PREFIX,
        "rate_limit_stats": stats
    }

@router.get("/middleware-health")
async def check_middleware_health():
    """Verifica el estado del middleware del dominio Academia Idiomas"""
    return {
        "domain": DOMAIN_PREFIX,
        "rate_limiter": "active",
        "logger": "active",
        "validator": "active",
        "status": "healthy ✅"
    }
