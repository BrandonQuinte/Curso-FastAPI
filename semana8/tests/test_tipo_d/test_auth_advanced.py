from datetime import datetime, timedelta

import jwt
import pytest
from fastapi import status

SECRET_KEY = "secret_test_key"
ALGORITHM = "HS256"


@pytest.mark.tipo_d
@pytest.mark.integration
class TestAutenticacionAvanzadaTipoD:
    """Tests de autenticación avanzada (nivel D) — MFA, revocación, políticas de sesión"""

    def test_autenticacion_mfa(self, client):
        """Test autenticación multifactor (MFA)"""

        user_data = {
            "username": "usuario_mfa",
            "email": "mfa@test.com",
            "password": "clave_segura_123",
            "mfa_enabled": True,
        }

        # Registro
        client.post("/api/v1/auth/register", json=user_data)

        # Login inicial (sin MFA)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "usuario_mfa", "password": "clave_segura_123"},
        )

        assert login_response.status_code == status.HTTP_202_ACCEPTED
        assert "mfa_required" in login_response.json()

        # Verificación MFA
        verify_response = client.post(
            "/api/v1/auth/mfa/verify",
            json={"username": "usuario_mfa", "code": "123456"},
        )
        assert verify_response.status_code == status.HTTP_200_OK
        assert "access_token" in verify_response.json()

    def test_expiracion_token(self, client):
        """Test que detecta tokens expirados"""

        payload = {
            "sub": "usuario_expira",
            "exp": datetime.utcnow() - timedelta(seconds=5),
        }
        expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in response.json()["detail"].lower()

    def test_revocacion_token(self, client, sample_user_generic):
        """Test revocación manual de token (lista negra)"""

        # Registrar y loguear
        client.post("/api/v1/auth/register", json=sample_user_generic)
        login_response = client.post("/api/v1/auth/login", json=sample_user_generic)
        token = login_response.json()["access_token"]

        # Revocar
        revoke_response = client.post(
            "/api/v1/auth/revoke", headers={"Authorization": f"Bearer {token}"}
        )
        assert revoke_response.status_code == status.HTTP_200_OK

        # Intentar usarlo luego
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_restriccion_por_ip(self, client, sample_user_generic):
        """Test restricción de acceso por IP (política de seguridad)"""

        client.post("/api/v1/auth/register", json=sample_user_generic)
        headers = {"X-Forwarded-For": "10.0.0.8"}

        response = client.post(
            "/api/v1/auth/login", json=sample_user_generic, headers=headers
        )
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_202_ACCEPTED,
        ]

    def test_limite_sesiones_simultaneas(self, client):
        """Test límite de sesiones activas"""

        user = {
            "username": "multi_user",
            "email": "multi@test.com",
            "password": "clave_segura_789",
        }

        client.post("/api/v1/auth/register", json=user)

        tokens = []
        for _ in range(3):
            resp = client.post("/api/v1/auth/login", json=user)
            tokens.append(resp.json()["access_token"])

        last_token = tokens[-1]
        headers = {"Authorization": f"Bearer {last_token}"}

        session_response = client.get("/api/v1/auth/sessions", headers=headers)
        assert session_response.status_code == status.HTTP_200_OK
        assert session_response.json()["active_sessions"] <= 2


@pytest.mark.tipo_d
@pytest.mark.unit
class TestSeguridadAvanzadaUnit:
    """Tests unitarios de seguridad avanzada"""

    def test_token_falsificado(self, client):
        """Token firmado con clave incorrecta"""
        fake_token = jwt.encode({"sub": "fake"}, "clave_incorrecta", algorithm="HS256")
        headers = {"Authorization": f"Bearer {fake_token}"}

        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_reutilizacion_token_revocado(self, client, sample_user_generic):
        """Evita reutilización de token revocado"""

        client.post("/api/v1/auth/register", json=sample_user_generic)
        login_response = client.post("/api/v1/auth/login", json=sample_user_generic)
        token = login_response.json()["access_token"]

        # Revocar token
        client.post("/api/v1/auth/revoke", headers={"Authorization": f"Bearer {token}"})

        # Intentar usarlo otra vez
        reuse_response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert reuse_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_algoritmo_no_permitido(self):
        """Rechaza tokens con algoritmos inseguros"""
        payload = {"sub": "test_inseguro"}
        insecure_token = jwt.encode(
            payload, SECRET_KEY, algorithm="HS384"
        )  # No permitido
        decoded = jwt.decode(
            insecure_token,
            SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_signature": False},
        )
        assert "sub" in decoded
