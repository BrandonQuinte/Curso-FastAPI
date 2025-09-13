import pytest
import uuid
import copy
from fastapi.testclient import TestClient


class TestDesignAPI:

    def test_get_all_proyectos(self, client, auth_headers):
        """Test de consulta de todas las entidades en Diseño Gráfico"""
        response = client.get("/design_proyectos/", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_proyecto_not_found(self, client, auth_headers):
        """Test de entidad no encontrada en Diseño Gráfico"""
        response = client.get("/design_proyectos/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "proyecto no encontrado" in response.json()["detail"].lower()

    def test_create_proyecto_success(self, client, sample_proyecto_data, auth_headers):
        """Test de creación exitosa de proyecto en Diseño Gráfico"""
        unique_data = copy.deepcopy(sample_proyecto_data)
        unique_data["nombre"] += f"_{uuid.uuid4().hex}"
        unique_data["cliente"] += f"_{uuid.uuid4().hex}"
        response = client.post("/design_proyectos/", json=unique_data, headers=auth_headers)
        assert response.status_code == 201, f"Project creation failed: {response.text}"
        data = response.json()
        assert data["nombre"] == unique_data["nombre"]
        assert data["cliente"] == unique_data["cliente"]
        assert data["descripcion"] == unique_data["descripcion"]

    def test_create_proyecto_duplicate(self, client, auth_headers):
        """Test de creación duplicada específico para Diseño Gráfico"""
        import uuid
        unique_nombre = f"Proyecto Duplicado {uuid.uuid4().hex}"
        unique_cliente = f"Cliente Duplicado {uuid.uuid4().hex}"
        data = {
            "nombre": unique_nombre,
            "cliente": unique_cliente,
            "descripcion": "Intento duplicado",
            "fecha_inicio": "2025-09-15",
            "fecha_entrega": "2025-09-25",
            "estado": "en_progreso"
        }
        # Crear primera vez
        response1 = client.post("/design_proyectos/", json=data, headers=auth_headers)
        assert response1.status_code == 201, f"Project creation failed: {response1.text}"
        # Intentar crear duplicado
        response2 = client.post("/design_proyectos/", json=data, headers=auth_headers)
        assert response2.status_code == 400
        assert "ya existe" in response2.json()["detail"].lower()

    def test_get_proyecto_by_id(self, client, auth_headers):
        """Test de consulta por ID específico para Diseño Gráfico"""
        create_data = {
            "nombre": f"Proyecto Consulta ID {uuid.uuid4().hex}",
            "cliente": f"Cliente Consulta {uuid.uuid4().hex}",
            "descripcion": "Proyecto para test de consulta por ID",
            "fecha_inicio": "2025-09-15",
            "fecha_entrega": "2025-09-25",
            "estado": "en_progreso"
        }
        create_response = client.post("/design_proyectos/", json=create_data, headers=auth_headers)
        assert create_response.status_code == 201, f"Project creation failed: {create_response.text}"
        created_id = create_response.json()["id"]
        response = client.get(f"/design_proyectos/{created_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_id

    def test_update_proyecto_complete(self, client, auth_headers):
        """Test de actualización completa para Diseño Gráfico"""
        create_data = {
            "nombre": f"Proyecto Original {uuid.uuid4().hex}",
            "cliente": f"Cliente Original {uuid.uuid4().hex}",
            "descripcion": "Descripción original",
            "fecha_inicio": "2025-09-10",
            "fecha_entrega": "2025-09-20",
            "estado": "en_progreso"
        }
        create_response = client.post("/design_proyectos/", json=create_data, headers=auth_headers)
        assert create_response.status_code == 201, f"Project creation failed: {create_response.text}"
        entity_id = create_response.json()["id"]

        update_data = {
            "nombre": f"Proyecto Actualizado {uuid.uuid4().hex}",
            "cliente": f"Cliente Actualizado {uuid.uuid4().hex}",
            "descripcion": "Descripción actualizada",
            "fecha_inicio": "2025-09-11",
            "fecha_entrega": "2025-09-21",
            "estado": "finalizado"
        }
        response = client.put(f"/design_proyectos/{entity_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200, f"Update failed: {response.text}"
        updated = response.json()
        assert updated["nombre"] == update_data["nombre"]
        assert updated["estado"] == update_data["estado"]

    def test_delete_proyecto_success(self, client):
        """Test de eliminación exitosa en Diseño Gráfico (con usuario admin)"""
        import uuid
        # Registrar y loguear usuario admin_design
        register_data = {
            "username": "admin_design",
            "password": "admin123",
            "role": "admin"
        }
        reg_resp = client.post("/auth/register", json=register_data)
        assert reg_resp.status_code in (201, 400), f"Register failed: {reg_resp.text}"
        login_resp = client.post("/auth/login", json={"username": "admin_design", "password": "admin123"})
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        create_data = {
            "nombre": f"Proyecto a eliminar {uuid.uuid4().hex}",
            "cliente": f"Cliente Eliminar {uuid.uuid4().hex}",
            "descripcion": "Proyecto para eliminar",
            "fecha_inicio": "2025-09-10",
            "fecha_entrega": "2025-09-20",
            "estado": "en_progreso"
        }
        create_response = client.post("/design_proyectos/", json=create_data, headers=headers)
        assert create_response.status_code == 201, f"Project creation failed: {create_response.text}"
        entity_id = create_response.json()["id"]
        response = client.delete(f"/design_proyectos/{entity_id}", headers=headers)
        assert response.status_code == 200, f"Delete failed: {response.text}"
        get_response = client.get(f"/design_proyectos/{entity_id}", headers=headers)
        assert get_response.status_code == 404

    def test_delete_proyecto_not_found(self, client, auth_headers):
        """Test de eliminación de entidad inexistente en Diseño Gráfico"""
        response = client.delete("/design_proyectos/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_proyecto_business_rules(self, client, auth_headers):
        """Test de reglas de negocio específicas para Diseño Gráfico"""
        invalid_data = {
            "nombre": "",
            "cliente": "Cliente inválido",
            "descripcion": "Descripción inválida",
            "fecha_inicio": "2025-09-10",
            "fecha_entrega": "2025-09-20",
            "estado": "en_progreso"
        }
        response = client.post("/design_proyectos/", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422
