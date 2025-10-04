# tests/test_tipo_d/test_endpoints_tipo_d.py
from datetime import datetime

import pytest
from fastapi import status


@pytest.mark.tipo_d
@pytest.mark.integration
class TestCatalogoEndpointsTipoD:
    """Tests completos de endpoints para Catálogo de Elementos (Tipo D)"""

    def test_crud_completo_propiedad(
        self, authenticated_client, sample_elemento_catalogo
    ):
        """Test CRUD completo de una propiedad inmobiliaria"""

        # CREATE
        create_response = authenticated_client.post(
            "/api/v1/catalogo", json=sample_elemento_catalogo
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        created_data = create_response.json()
        propiedad_id = created_data["id"]

        # Validar campos iniciales
        assert created_data["nombre"] == sample_elemento_catalogo["nombre"]
        assert created_data["categoria"] == sample_elemento_catalogo["categoria"]
        assert "fecha_creacion" in created_data
        assert "fecha_actualizacion" in created_data

        # READ
        read_response = authenticated_client.get(f"/api/v1/catalogo/{propiedad_id}")
        assert read_response.status_code == status.HTTP_200_OK
        read_data = read_response.json()
        assert read_data["id"] == propiedad_id

        # UPDATE
        update_data = {
            "nombre": "Apartamento Remodelado Premium",
            "precio": 1450000,
            "estado": "reservado",
        }
        update_response = authenticated_client.put(
            f"/api/v1/catalogo/{propiedad_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK

        updated = update_response.json()
        assert updated["nombre"] == "Apartamento Remodelado Premium"
        assert updated["estado"] == "reservado"
        assert updated["fecha_actualizacion"] != created_data["fecha_actualizacion"]

        # DELETE
        delete_response = authenticated_client.delete(
            f"/api/v1/catalogo/{propiedad_id}"
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar eliminación
        verify_response = authenticated_client.get(f"/api/v1/catalogo/{propiedad_id}")
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    def test_busqueda_y_filtros(
        self, authenticated_client, multiple_elementos_catalogo
    ):
        """Test búsqueda avanzada y filtros múltiples"""

        for item in multiple_elementos_catalogo:
            authenticated_client.post("/api/v1/catalogo", json=item)

        response = authenticated_client.get(
            "/api/v1/catalogo/buscar",
            params={"categoria": "Apartamento", "disponible": True},
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

        for item in data["items"]:
            assert item["disponible"] is True

    def test_paginacion_catalogo(self, authenticated_client):
        """Test paginación del catálogo inmobiliario"""

        for i in range(25):
            propiedad = {
                "nombre": f"Propiedad {i}",
                "categoria": "Apartamento",
                "precio": 100000 + i * 10000,
                "disponible": True,
            }
            authenticated_client.post("/api/v1/catalogo", json=propiedad)

        # Página 1
        page1 = authenticated_client.get(
            "/api/v1/catalogo", params={"skip": 0, "limit": 10}
        )
        assert page1.status_code == status.HTTP_200_OK
        page1_data = page1.json()
        assert len(page1_data["items"]) == 10
        assert page1_data["page"] == 1

        # Página 2
        page2 = authenticated_client.get(
            "/api/v1/catalogo", params={"skip": 10, "limit": 10}
        )
        page2_data = page2.json()
        assert page2.status_code == status.HTTP_200_OK
        assert page2_data["page"] == 2
        assert len(page2_data["items"]) == 10

        # Sin duplicados
        ids1 = [i["id"] for i in page1_data["items"]]
        ids2 = [i["id"] for i in page2_data["items"]]
        assert len(set(ids1) & set(ids2)) == 0

    def test_validaciones_catalogo(self, authenticated_client):
        """Test validaciones específicas del catálogo"""

        # Precio negativo
        invalid_data = {"nombre": "Casa Error", "categoria": "Casa", "precio": -20000}
        response = authenticated_client.post("/api/v1/catalogo", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Campo obligatorio ausente
        invalid_data2 = {"descripcion": "Sin nombre ni categoría"}
        response2 = authenticated_client.post("/api/v1/catalogo", json=invalid_data2)
        assert response2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_soft_delete_catalogo(self, authenticated_client, sample_elemento_catalogo):
        """Test de eliminación suave (soft delete)"""

        create_resp = authenticated_client.post(
            "/api/v1/catalogo", json=sample_elemento_catalogo
        )
        propiedad_id = create_resp.json()["id"]

        delete_resp = authenticated_client.delete(f"/api/v1/catalogo/{propiedad_id}")
        assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

        # No debe aparecer en listado activo
        list_resp = authenticated_client.get("/api/v1/catalogo")
        active_ids = [item["id"] for item in list_resp.json()["items"]]
        assert propiedad_id not in active_ids

        # Debe aparecer si se listan los eliminados
        deleted_resp = authenticated_client.get(
            "/api/v1/catalogo", params={"incluir_eliminados": True}
        )
        all_ids = [item["id"] for item in deleted_resp.json()["items"]]
        assert propiedad_id in all_ids


@pytest.mark.tipo_d
@pytest.mark.unit
class TestValidacionesTipoD:
    """Tests unitarios de validaciones del catálogo (Tipo D)"""

    def test_validacion_campos_requeridos(self, authenticated_client):
        """Validar campos requeridos del catálogo"""
        invalid_data = {"precio": 100000}
        response = authenticated_client.post("/api/v1/catalogo", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validacion_tipos_datos(self, authenticated_client):
        """Validar tipos de datos incorrectos"""
        invalid_data = {
            "nombre": "Oficina Central",
            "categoria": "Oficina",
            "precio": "texto_no_valido",
        }
        response = authenticated_client.post("/api/v1/catalogo", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_longitud_campos(self, authenticated_client):
        """Validar longitudes máximas de texto"""
        invalid_data = {
            "nombre": "x" * 300,
            "categoria": "Apartamento",
            "descripcion": "y" * 3000,
        }
        response = authenticated_client.post("/api/v1/catalogo", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
