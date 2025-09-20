# app/main.py
from fastapi import FastAPI
import redis

# Middlewares
from .middleware.domain_rate_limiter import DomainRateLimiter
from .middleware.domain_logger import DomainLogger
from .middleware.domain_validator import DomainValidator

# Routers
from .routers import optimized_domain_routes

# Dominio: Academia Idiomas
DOMAIN_PREFIX = "lang_"  # Prefijo definido para este dominio

app = FastAPI(
    title=f"API Optimizada - Academia Idiomas ({DOMAIN_PREFIX.upper()})",
    description="Microservicio optimizado para cursos, niveles y grupos en Academia de Idiomas"
)

# Configuración de Redis (para rate limiting y caching si se requiere)
redis_client = redis.Redis(host="localhost", port=6379, db=0)

# Middleware específico del dominio (orden importa: validación → logging → rate limiting)
app.add_middleware(DomainValidator, domain_prefix=DOMAIN_PREFIX)
app.add_middleware(DomainLogger, domain_prefix=DOMAIN_PREFIX)
app.add_middleware(DomainRateLimiter, domain_prefix=DOMAIN_PREFIX, redis_client=redis_client)

# Incluir routers optimizados del dominio
app.include_router(optimized_domain_routes.router)

# Healthcheck simple
@app.get("/health")
def healthcheck():
    return {
        "status": "ok",
        "domain": DOMAIN_PREFIX,
        "message": "API de Academia Idiomas funcionando correctamente ✅"
    }
