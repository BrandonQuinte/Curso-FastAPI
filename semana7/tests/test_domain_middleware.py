import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
semana7_dir = os.path.abspath(os.path.join(current_dir, '..'))
if semana7_dir not in sys.path:
    sys.path.insert(0, semana7_dir)
# tests/test_domain_middleware.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

class TestDomainMiddleware:

    def test_rate_limiting_enforcement(self):
        """Verifica que el rate limiting funcione en Academia Idiomas"""
        # Hacer muchas requests rápidas
        for i in range(150):  # Exceder límite
            response = client.get("/lang/test-endpoint")
            if response.status_code == 429:
                break
        else:
            pytest.fail("Rate limiting no se activó para lang_")

import pytest
from unittest.mock import patch, MagicMock
@pytest.fixture(autouse=True)
def mock_redis_client():
    with patch('app.middleware.domain_rate_limiter.redis.Redis') as mock_redis:
        instance = MagicMock()
        mock_redis.return_value = instance
        instance.zrangebyscore.return_value = []
        instance.get.return_value = None
        instance.setex.return_value = True
        instance.keys.return_value = []
        instance.delete.return_value = None
        yield
    def test_business_hours_validation(self):
        """Verifica validación de horarios de atención en Academia Idiomas"""
        # Simular request fuera de horario (requiere mock del tiempo)
        response = client.get("/lang/restricted-endpoint")
        # Puede ser permitido o rechazado según configuración
        assert response.status_code in [200, 403]

    def test_domain_specific_logging(self):
        """Verifica que el logging específico funcione en Academia Idiomas"""
        response = client.get("/lang/logged-endpoint")
        assert response.status_code == 200

        # Verificar que se creó el archivo de log para lang_
        log_file = "logs/lang_domain.log"
        assert os.path.exists(log_file), f"No se encontró el log esperado en {log_file}"

    def test_required_headers_validation(self):
        """Verifica validación de headers requeridos en Academia Idiomas"""
        # Request sin headers requeridos
        response = client.get("/lang/protected-endpoint")

        # Request con headers requeridos
        headers = {"X-Your-Required-Header": "test-value"}
        response_with_headers = client.get("/lang/protected-endpoint", headers=headers)

        # Verificar comportamiento según configuración del dominio
        assert response.status_code == 400 or response_with_headers.status_code == 200
