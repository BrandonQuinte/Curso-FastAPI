# tests/utils/test_helpers.py
from typing import Any, Dict, List

from fastapi.testclient import TestClient


class APITestHelper:
    """Helper genérico para testing de APIs — adaptado a RealEstate"""

    def __init__(self, client: TestClient, auth_headers: Dict[str, str]):
        self.client = client
        self.auth_headers = auth_headers

    def create_and_get_id(self, endpoint: str, data: Dict[str, Any]) -> int:
        """Crear recurso (ej: propiedad) y retornar ID"""
        response = self.client.post(endpoint, json=data, headers=self.auth_headers)
        assert response.status_code in [
            200,
            201,
        ], f"Error creando recurso en {endpoint}"
        return response.json().get("id")

    def assert_pagination_response(self, response_data: Dict[str, Any]):
        """Validar estructura de respuesta paginada"""
        assert all(k in response_data for k in ["items", "total", "page", "limit"])
        assert isinstance(response_data["items"], list)
        assert isinstance(response_data["total"], int)

    def assert_error_response(
        self, response_data: Dict[str, Any], error_code: str = None
    ):
        """Validar estructura de error estándar"""
        assert "detail" in response_data
        if error_code:
            assert error_code in response_data.get("error_code", "")

    def create_multiple_resources(
        self, endpoint: str, data_list: List[Dict[str, Any]]
    ) -> List[int]:
        """Crear múltiples recursos (ej: propiedades)"""
        ids = []
        for data in data_list:
            resource_id = self.create_and_get_id(endpoint, data)
            ids.append(resource_id)
        return ids


def assert_valid_datetime_format(datetime_string: str):
    """Validar formato de datetime ISO"""
    from datetime import datetime

    try:
        datetime.fromisoformat(datetime_string.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def assert_response_schema(response_data: Dict[str, Any], required_fields: List[str]):
    """Validar que response contiene los campos requeridos"""
    for field in required_fields:
        assert (
            field in response_data
        ), f"Campo requerido '{field}' no encontrado en response"


def generate_test_pagination_params():
    """Generar parámetros de paginación estándar"""
    return [
        {"skip": 0, "limit": 10},
        {"skip": 5, "limit": 5},
        {"skip": 0, "limit": 1},
        {"skip": 10, "limit": 10},
    ]
