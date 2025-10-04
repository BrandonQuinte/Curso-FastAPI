# tests/test_auth.py
import pytest
from fastapi import status


@pytest.mark.auth
@pytest.mark.unit
class TestAutenticacionRealEstate:
    """Tests de autenticación en Inmobiliaria Premium RealEstate"""

    def test_login_credenciales_validas(self, client, sample_user_realestate):
        """✅ Login con credenciales válidas"""
        # Crear usuario
        client.post("/api/v1/auth/register", json=sample_user_realestate)

        login_data = {
            "username": sample_user_realestate["username"],
            "password": sample_user_realestate["password"],
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_credenciales_invalidas(self, client):
        """❌ Login con credenciales inválidas"""
        login_data = {"username": "usuario_inexistente", "password": "incorrecto123"}
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    def test_acceso_sin_token(self, client):
        """🚫 Acceso sin token a endpoint protegido"""
        response = client.get("/api/v1/propiedades")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_acceso_token_invalido(self, client):
        """🚫 Acceso con token inválido"""
        headers = {"Authorization": "Bearer token_invalido"}
        response = client.get("/api/v1/propiedades", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
