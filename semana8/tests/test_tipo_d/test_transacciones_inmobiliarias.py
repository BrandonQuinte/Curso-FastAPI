import pytest
from fastapi import status

@pytest.mark.tipo_d
@pytest.mark.integration
class TestTransaccionesInmobiliarias:
    """Tests de transacciones inmobiliarias genéricas"""

    def test_crear_transaccion_compra(self, client, sample_elemento_tipo_d, sample_transaccion_tipo_d, auth_headers):
        """Crear transacción tipo 'compra'"""
        # Crear elemento (propiedad)
        propiedad_resp = client.post(
            "/api/v1/propiedades",
            json=sample_elemento_tipo_d,
            headers=auth_headers
        )
        propiedad_id = propiedad_resp.json()["id"]

        # Crear transacción
        transaccion_data = {**sample_transaccion_tipo_d, "elemento_id": propiedad_id}
        response = client.post(
            "/api/v1/transacciones",
            json=transaccion_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["elemento_id"] == propiedad_id
        assert data["tipo_transaccion"] in ["compra", "venta", "devolucion"]

    def test_listar_transacciones(self, client, auth_headers, pagination_params):
        """Listar transacciones con paginación"""
        response = client.get(
            "/api/v1/transacciones",
            params=pagination_params,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_eliminar_transaccion(self, client, sample_elemento_tipo_d, sample_transaccion_tipo_d, auth_headers):
        """Eliminar transacción existente"""
        propiedad_resp = client.post(
            "/api/v1/propiedades",
            json=sample_elemento_tipo_d,
            headers=auth_headers
        )
        propiedad_id = propiedad_resp.json()["id"]

        transaccion_data = {**sample_transaccion_tipo_d, "elemento_id": propiedad_id}
        trans_resp = client.post(
            "/api/v1/transacciones",
            json=transaccion_data,
            headers=auth_headers
        )
        transaccion_id = trans_resp.json()["id"]

        response = client.delete(f"/api/v1/transacciones/{transaccion_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
