# tests/test_performance.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import status  # ✅ Falta este import


@pytest.mark.slow
@pytest.mark.benchmark
class TestPerformanceAPI:
    """Tests básicos de performance para endpoints"""

    def test_response_time_endpoints(self, authenticated_client, benchmark):
        """Test tiempo de respuesta de endpoints principales"""

        def get_entidades():
            return authenticated_client.get("/api/v1/entidades")

        # Benchmark automático con pytest-benchmark
        response = benchmark(get_entidades)
        assert response.status_code == status.HTTP_200_OK

        # El benchmark automáticamente reportará estadísticas

    def test_concurrent_requests(self, authenticated_client):
        """Test manejo de requests concurrentes"""

        def make_request():
            response = authenticated_client.get("/api/v1/entidades")
            return response.status_code

        # Ejecutar 10 requests concurrentes
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]

        # Todos los requests deben ser exitosos
        assert all(status_code == 200 for status_code in results)

    def test_large_payload_handling(self, authenticated_client):
        """Test manejo de payloads grandes"""

        # Crear entidad con datos grandes
        large_data = {
            "nombre": "Entidad con datos grandes",
            "categoria": "test",
            "descripcion": "x" * 1000,  # 1KB de descripción
            "propiedades": {
                f"propiedad_{i}": f"valor_largo_{'x' * 100}"
                for i in range(50)  # 50 propiedades
            },
        }

        start_time = time.time()
        response = authenticated_client.post("/api/v1/entidades", json=large_data)
        end_time = time.time()

        assert response.status_code == status.HTTP_201_CREATED
        assert (end_time - start_time) < 5.0  # Menos de 5 segundos
