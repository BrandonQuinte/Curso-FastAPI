import os
import logging
import json
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any, Tuple

class DomainLogger(BaseHTTPMiddleware):
    def __init__(self, app, domain_prefix: str):
        super().__init__(app)
        self.domain_prefix = domain_prefix

        # Asegurar carpeta de logs
        os.makedirs("logs", exist_ok=True)

        # Configurar logger específico para el dominio
        self.logger = logging.getLogger(f"{domain_prefix}domain_logger")
        self.logger.setLevel(logging.INFO)

        # Evitar múltiples handlers
        if not self.logger.handlers:
            handler = logging.FileHandler(f"logs/{domain_prefix}domain.log")
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Configurar qué endpoints loggear por dominio
        self.logged_endpoints = self._get_logged_endpoints(domain_prefix)

    def _get_logged_endpoints(self, domain_prefix: str) -> Dict[str, str]:
        """Define qué endpoints requieren logging específico por dominio"""

        logging_configs = {
            "vet_": {
                "/historial": "CRITICAL",
                "/emergency": "CRITICAL",
                "/update": "WARNING",
                "/delete": "CRITICAL",
            },
            "edu_": {
                "/booking": "INFO",
                "/schedule": "INFO",
                "/enrollment": "WARNING",
                "/admin": "WARNING",
            },
            "gym_": {
                "/checkin": "INFO",
                "/equipment": "INFO",
                "/membership": "WARNING",
                "/access": "INFO",
            },
            "pharma_": {
                "/inventory": "INFO",
                "/sales": "WARNING",
                "/price": "INFO",
                "/admin": "CRITICAL",
            },
            "lang_": {  # 💡 Academia de Idiomas
                "/cursos": "INFO",
                "/niveles": "INFO",
                "/grupos": "WARNING",
                "/admin": "CRITICAL",
            }
        }

        return logging_configs.get(domain_prefix, {
            "/create": "INFO",
            "/update": "WARNING",
            "/delete": "CRITICAL",
            "/admin": "WARNING"
        })

    def _should_log_endpoint(self, path: str) -> Tuple[bool, str]:
        """Determina si el endpoint debe ser loggeado y su nivel"""
        for endpoint_pattern, level in self.logged_endpoints.items():
            if endpoint_pattern in path:
                return True, level
        return False, "INFO"

    def _extract_domain_specific_data(self, request: Request, path: str) -> Dict[str, Any]:
        """Extrae datos específicos del dominio para logging"""
        data = {
            "domain": self.domain_prefix,
            "path": path,
            "method": request.method,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", "unknown")
        }

        if self.domain_prefix == "lang_":
            if "curso_id" in str(request.url):
                data["entity_type"] = "curso"
            elif "nivel_id" in str(request.url):
                data["entity_type"] = "nivel"
            elif "grupo_id" in str(request.url):
                data["entity_type"] = "grupo"

        return data

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        path = request.url.path

        if not path.startswith(f"/{self.domain_prefix.rstrip('_')}"):
            return await call_next(request)

        should_log, log_level = self._should_log_endpoint(path)

        if should_log:
            request_data = self._extract_domain_specific_data(request, path)
            self.logger.log(
                getattr(logging, log_level),
                f"REQUEST_START: {json.dumps(request_data)}"
            )

        response = await call_next(request)

        if should_log:
            process_time = time.time() - start_time
            response_data = {
                **request_data,
                "status_code": response.status_code,
                "process_time": round(process_time, 3)
            }

            if response.status_code >= 500:
                response_level = "CRITICAL"
            elif response.status_code >= 400:
                response_level = "WARNING"
            else:
                response_level = log_level

            self.logger.log(
                getattr(logging, response_level),
                f"REQUEST_END: {json.dumps(response_data)}"
            )

        return response
