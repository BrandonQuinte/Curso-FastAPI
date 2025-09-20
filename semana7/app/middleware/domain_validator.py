# app/middleware/domain_validator.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any, Optional
from datetime import datetime

class DomainValidator(BaseHTTPMiddleware):
    def __init__(self, app, domain_prefix: str):
        super().__init__(app)
        self.domain_prefix = domain_prefix
        self.validators = self._get_domain_validators(domain_prefix)

    def _get_domain_validators(self, domain_prefix: str) -> Dict[str, Any]:
        """Validadores específicos por dominio"""
        configs = {
            "vet_": {
                "required_headers": ["X-Vet-License"],
                "business_hours": (8, 20),
                "exceptions": {"emergency": True}
            },
            "edu_": {
                "required_headers": ["X-Institution-ID"],
                "business_hours": (6, 22),
                "weekend_restricted": ["booking"]
            },
            "gym_": {
                "required_headers": ["X-Gym-Membership"],
                "business_hours": (5, 23),
                "capacity_limits": True
            },
            "pharma_": {
                "required_headers": ["X-Pharmacy-License"],
                "business_hours": (7, 21),
                "prescription_required": ["controlled"],
                "exceptions": {"emergency": True}
            }
        }
        return configs.get(domain_prefix, {
            "required_headers": [],
            "business_hours": (0, 24)
        })

    def _validate_business_hours(self, path: str) -> bool:
        """Valida horarios de atención"""
        current_hour = datetime.now().hour
        start_hour, end_hour = self.validators.get("business_hours", (0, 24))

        # Manejo de rangos que cruzan medianoche
        if start_hour <= end_hour:
            in_hours = start_hour <= current_hour <= end_hour
        else:
            in_hours = current_hour >= start_hour or current_hour <= end_hour

        # Excepciones por path
        if self.validators.get("exceptions", {}).get("emergency") and "/emergency" in path:
            return True

        return in_hours

    def _validate_required_headers(self, request: Request) -> bool:
        """Valida headers requeridos"""
        required = [h.lower() for h in self.validators.get("required_headers", [])]
        request_headers = {k.lower() for k in request.headers.keys()}
        return all(h in request_headers for h in required)

    def _validate_domain_specific_rules(self, request: Request, path: str) -> tuple[bool, Optional[str]]:
        """Validaciones adicionales"""
        if self.domain_prefix == "edu_":
            if any(r in path for r in self.validators.get("weekend_restricted", [])):
                if datetime.now().weekday() >= 5:
                    return False, "Reservas no disponibles en fin de semana"

        if self.domain_prefix == "pharma_":
            if any(r in path for r in self.validators.get("prescription_required", [])):
                if "X-Prescription-ID" not in request.headers:
                    return False, "Medicamento controlado requiere prescripción"

        # TODO: implementar control de capacidad para gym_
        return True, None

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Solo validar rutas de este dominio
        if not path.startswith(f"/{self.domain_prefix.rstrip('_')}"):
            return await call_next(request)

        if not self._validate_business_hours(path):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Fuera de horario de atención",
                    "allowed_hours": self.validators["business_hours"]
                }
            )

        if not self._validate_required_headers(request):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Headers requeridos faltantes",
                    "required_headers": self.validators["required_headers"]
                }
            )

        is_valid, error_message = self._validate_domain_specific_rules(request, path)
        if not is_valid:
            raise HTTPException(status_code=422, detail={"error": error_message})

        return await call_next(request)
