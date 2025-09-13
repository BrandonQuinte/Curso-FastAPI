import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from database import Base

# Base de datos de prueba para Diseño Gráfico
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_design_.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def session(db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# FIXTURE PARA PROYECTO (Diseño Gráfico)
@pytest.fixture
def sample_proyecto_data():
    """
    Datos de ejemplo para entidad 'proyecto' en el dominio Diseño Gráfico
    """
    return {
        "nombre": "Diseños Gráficos: Rock Legends 90s",
        "cliente": "Rockventero Shirts Co",
        "descripcion": "Diseño de ilustraciones originales para camisetas de bandas iconicas del rock ochentero con estilo glam y grunge.",
        "fecha_inicio": "2025-09-10",
        "fecha_entrega": "2025-09-20",
        "estado": "en_progreso"
    }

@pytest.fixture
def auth_headers(client):
    """Headers de autenticación para tests"""
    # Crear usuario de prueba para Diseño Gráfico
    response = client.post("/auth/register", json={
        "username": "admin_design_",
        "password": "test123",
        "role": "admin"
    })

    login_response = client.post("/auth/login", data={
        "username": "admin_design_",
        "password": "test123"
    })

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
