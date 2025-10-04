import pytest
from fastapi import status

@pytest.mark.tipo_d
@pytest.mark.integration
class TestCatalogoInmobiliarioCRUD:
    """Tests CRUD para elementos del catálogo inmobiliario (Tipo D)"""

    def test_crear_propiedad_valida(self, client, sample_elemento_tipo_d, auth_headers):
        """Crear una propiedad válida"""
        response = client.post(
            "/api/v1/propiedades",
            json=sample_elemento_tipo_d,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["nombre"] == sample_elemento_tipo_d["nombre"]
        assert data["categoria"] in ["electronica", "ropa", "hogar", "deportes"]  # genérico base, reemplazar luego
        assert data["disponible"] is True

    def test_listar_propiedades_con_paginacion(self, client, auth_headers, pagination_params):
        """Listar propiedades con paginación estándar"""
        response = client.get(
            "/api/v1/propiedades",
            params=pagination_params,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        assert "total" in data
        assert isinstance(data["total"], int)

    def test_obtener_propiedad_por_id(self, client, auth_headers):
        """Obtener una propiedad existente por ID"""
        create_data = {
            "nombre": "Apartamento Central Park",
            "descripcion": "Apartamento moderno en el centro",
            "categoria": "vivienda",
            "precio": 350000.00,
            "stock": 1,
            "disponible": True
        }

        create_response = client.post(
            "/api/v1/propiedades",
            json=create_data,
            headers=auth_headers
        )
        propiedad_id = create_response.json()["id"]

        response = client.get(f"/api/v1/propiedades/{propiedad_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == propiedad_id
        assert data["nombre"] == "Apartamento Central Park"

    def test_actualizar_propiedad_existente(self, client, auth_headers):
        """Actualizar los datos de una propiedad"""
        create_data = {
            "nombre": "Casa Antigua",
            "categoria": "vivienda",
            "precio": 120000.00,
            "stock": 1,
            "disponible": True
        }

        create_response = client.post(
            "/api/v1/propiedades",
            json=create_data,
            headers=auth_headers
        )
        propiedad_id = create_response.json()["id"]

        update_data = {
            "nombre": "Casa Restaurada",
            "precio": 180000.00
        }

        response = client.put(
            f"/api/v1/propiedades/{propiedad_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == "Casa Restaurada"
        assert data["precio"] == 180000.00

    def test_eliminar_propiedad(self, client, auth_headers):
        """Eliminar una propiedad existente"""
        create_data = {
            "nombre": "Bodega Industrial",
            "categoria": "comercial",
            "precio": 750000.00,
            "stock": 1
        }

        create_response = client.post(
            "/api/v1/propiedades",
            json=create_data,
            headers=auth_headers
        )
        propiedad_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/propiedades/{propiedad_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        get_response = client.get(f"/api/v1/propiedades/{propiedad_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.tipo_d
@pytest.mark.unit
class TestValidacionesCatalogoInmobiliario:
    """Validaciones de campos y errores en catálogo inmobiliario"""

    def test_crear_propiedad_datos_invalidos(self, client, auth_headers):
        """Intentar crear una propiedad con datos inválidos"""
        invalid_data = {
            "nombre": "",
            "precio": -200,
            "stock": -5
        }

        response = client.post(
            "/api/v1/propiedades",
            json=invalid_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any("precio" in str(error) or "nombre" in str(error) for error in errors)

    def test_obtener_propiedad_inexistente(self, client, auth_headers):
        """Buscar propiedad inexistente"""
        response = client.get("/api/v1/propiedades/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "no encontrada" in response.json()["detail"].lower()
