from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from datetime import datetime
import time

from .docs.descriptions import TAGS_METADATA


# Configuración de la aplicación
app = FastAPI(
    title="API Tipo D - Inmobiliaria Premium RealEstate",
    description="""
    ## API Tipo D - Gestión de Usuarios

    API avanzada para la **administración de usuarios** del sistema Inmobiliaria Premium RealEstate.

    ### Funcionalidades principales:
    * **CRUD completo de usuarios**
    * **Roles y estados dinámicos**
    * **Filtros, paginación y búsqueda**
    * **Reportes de estadísticas**
    * **Validación de datos avanzada**

    ### Tipos de usuario:
    - Administrador
    - Editor
    - Agente
    - Cliente

    ### Autenticación:
    - En producción: basada en JWT
    - En desarrollo: libre (sin token requerido)

    ### Versionado:
    - **Versión 1.0** enfocada en administración de usuarios
    """,
    version="1.0.0",
    terms_of_service="https://realestate.com/terms",
    contact={
        "name": "Equipo Backend RealEstate",
        "url": "https://realestate.com/contact",
        "email": "devteam@realestate.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=TAGS_METADATA,
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/v1/openapi.json"
)


# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.realestate.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hosts permitidos
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "*.realestate.com"]
)


# Middleware de logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    response.headers["X-Timestamp"] = datetime.now().isoformat()
    return response



# Incluir router de autenticación
from app.auth.auth_router import router as auth_router
app.include_router(auth_router)


# Endpoint de salud
@app.get(
    "/health",
    tags=["sistema"],
    summary="Verificar estado de la API",
    description="Devuelve información básica sobre el estado de la API Tipo D."
)
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "api_name": "API Tipo D - RealEstate"
    }


# Configuración personalizada de OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )

    openapi_schema["info"]["x-logo"] = {"url": "https://realestate.com/logo.png"}

    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Servidor de desarrollo"},
        {"url": "https://api-staging.realestate.com", "description": "Servidor de staging"},
        {"url": "https://api.realestate.com", "description": "Servidor de producción"},
    ]

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT de autenticación",
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Clave API para autenticación",
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Documentación personalizada
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://realestate.com/favicon.ico",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
        redoc_favicon_url="https://realestate.com/favicon.ico",
    )


# Manejadores de errores personalizados
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "RECURSO_NO_ENCONTRADO",
            "mensaje": f"El recurso '{request.url.path}' no existe",
            "codigo_http": 404,
            "timestamp": datetime.now().isoformat(),
            "sugerencias": [
                "Verifique la URL solicitada",
                "Consulte la documentación en /docs",
            ],
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "ERROR_INTERNO_SERVIDOR",
            "mensaje": "Ocurrió un error interno en el servidor",
            "codigo_http": 500,
            "timestamp": datetime.now().isoformat(),
            "contacto": "devteam@realestate.com",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
