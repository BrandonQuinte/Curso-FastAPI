# tests/conftest.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker

from app.main import app
from app.database import get_db, Base
from app.auth.auth_handler import create_access_token

# ======================================================
# 🧩 CONFIGURACIÓN GENERAL DE PRUEBAS
# ======================================================

SQLALCHEMY_DATABASE_URL_TEST = "sqlite:///./test_realestate_tipo_d.db"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)

fake = Faker("es_ES")

# ======================================================
# 🔁 FIXTURES BASE
# ======================================================

@pytest.fixture(scope="session")
def event_loop():
    """Loop de eventos para pruebas async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Crea y destruye una sesión de BD SQLite de prueba"""
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de prueba FastAPI con base de datos temporal"""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()



# ======================================================
# 🔐 AUTENTICACIÓN DE PRUEBA
# ======================================================

@pytest.fixture
def auth_headers():
    """Crea headers con token JWT válido"""
    token_data = {"sub": "tester_inmobiliaria_premium"}
    token = create_access_token(token_data)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_user_realestate():
    """Usuario genérico para operaciones autenticadas"""
    return {
        "username": "agente_premium",
        "email": "agente@premiumrealestate.com",
        "password": "premium123",
        "is_active": True
    }

# --- NUEVO: sample_user_generic fixture para tests avanzados tipo D ---
@pytest.fixture
def sample_user_generic():
    """Usuario genérico para pruebas tipo D (registro/login)"""
    return {
        "username": "usuario_tipo_d",
        "email": "usuario_tipo_d@test.com",
        "password": "clave_segura_456",
        "is_active": True
    }

# --- NUEVO: authenticated_client fixture con debug ---
@pytest.fixture
def authenticated_client(client, sample_user_generic):
    """Cliente autenticado con registro y login previos. Imprime errores si ocurren."""
    # Registro
    reg_resp = client.post("/api/v1/auth/register", json=sample_user_generic)
    if reg_resp.status_code != 201:
        print("[REGISTER FAIL]", reg_resp.status_code, reg_resp.text)
    # Login
    login_data = {
        "username": sample_user_generic["username"],
        "password": sample_user_generic["password"]
    }
    login_resp = client.post("/api/v1/auth/login", json=login_data)
    if login_resp.status_code != 200:
        print("[LOGIN FAIL]", login_resp.status_code, login_resp.text)
    token = None
    try:
        token = login_resp.json().get("access_token")
    except Exception as e:
        print("[LOGIN JSON ERROR]", str(e), login_resp.text)
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    class AuthClient:
        def __init__(self, client, headers):
            self._client = client
            self._headers = headers
        def get(self, *args, **kwargs):
            if "headers" not in kwargs:
                kwargs["headers"] = self._headers
            return self._client.get(*args, **kwargs)
        def post(self, *args, **kwargs):
            if "headers" not in kwargs:
                kwargs["headers"] = self._headers
            return self._client.post(*args, **kwargs)
        def put(self, *args, **kwargs):
            if "headers" not in kwargs:
                kwargs["headers"] = self._headers
            return self._client.put(*args, **kwargs)
        def delete(self, *args, **kwargs):
            if "headers" not in kwargs:
                kwargs["headers"] = self._headers
            return self._client.delete(*args, **kwargs)
    return AuthClient(client, headers)

# ======================================================
# 🔐 USUARIO GENÉRICO PARA TESTS AVANZADOS (TIPO D)
# ======================================================

@pytest.fixture
def sample_user_generic():
    """Usuario genérico para autenticación avanzada (Tipo D)"""
    return {
        "username": "usuario_generico",
        "email": "generico@test.com",
        "password": "clave_segura_456",
        # Campos opcionales para compatibilidad con MFA y otros tests
        "mfa_enabled": False,
        "is_active": True
    }

# ======================================================
# 🏢 FIXTURES TIPO D — Catálogo de Elementos
# ======================================================

# ======================================================
# 🔐 CLIENTE AUTENTICADO PARA ENDPOINTS PROTEGIDOS
# ======================================================

@pytest.fixture
def authenticated_client(client, sample_user_generic):
    """Devuelve un TestClient autenticado con un usuario genérico tipo D."""
    # Registrar usuario
    client.post("/api/v1/auth/register", json=sample_user_generic)
    # Login para obtener token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "username": sample_user_generic["username"],
            "password": sample_user_generic["password"]
        }
    )
    token = login_resp.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.fixture
def sample_elemento_catalogo():
    """Elemento único del catálogo (propiedad inmobiliaria)"""
    return {
        "nombre": fake.street_name() + " " + fake.building_number(),
        "descripcion": fake.text(max_nb_chars=180),
        "categoria": fake.random_element(["Apartamento", "Casa", "Oficina", "Local"]),
        "ubicacion": fake.city(),
        "precio": round(fake.random.uniform(100000.0, 950000.0), 2),
        "area_m2": round(fake.random.uniform(35.0, 450.0), 2),
        "habitaciones": fake.random_int(1, 5),
        "banos": fake.random_int(1, 3),
        "garajes": fake.random_int(0, 2),
        "estado": fake.random_element(["disponible", "vendido", "reservado"]),
        "destacado": fake.boolean(),
        "disponible": True,
        "imagenes": [fake.image_url(), fake.image_url()]
    }


@pytest.fixture
def multiple_elementos_catalogo():
    """Genera una lista de varios elementos del catálogo"""
    return [
        {
            "nombre": fake.street_name() + " " + fake.building_number(),
            "categoria": fake.random_element(["Apartamento", "Casa"]),
            "ubicacion": fake.city(),
            "precio": round(fake.random.uniform(90000.0, 600000.0), 2),
            "area_m2": round(fake.random.uniform(40.0, 300.0), 2),
            "habitaciones": fake.random_int(1, 4),
            "banos": fake.random_int(1, 3),
            "disponible": True
        }
        for _ in range(5)
    ]

# ======================================================
# 🔎 FIXTURES DE CONSULTA / PAGINACIÓN / FILTROS
# ======================================================

@pytest.fixture
def pagination_params():
    """Parámetros estándar de paginación"""
    return {"skip": 0, "limit": 10, "sort_by": "precio", "sort_order": "asc"}


@pytest.fixture
def filter_params():
    """Filtros genéricos para catálogo"""
    return {
        "categoria": "Apartamento",
        "estado": "disponible",
        "precio_min": 100000,
        "precio_max": 800000
    }


@pytest.fixture
def search_params():
    """Búsqueda genérica de propiedades"""
    return {"search": "lujo"}
