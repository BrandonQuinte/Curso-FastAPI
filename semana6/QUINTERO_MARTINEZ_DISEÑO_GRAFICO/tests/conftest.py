import hashlib
from models import User
from database import SessionLocal
import pytest

@pytest.fixture(scope="session", autouse=True)
def create_test_user():
    db = SessionLocal()
    username = "testuser"
    password = "testpass"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = db.query(User).filter_by(username=username).first()
    if not user:
        user = User(username=username, hashed_password=hashed_password)
        db.add(user)
        db.commit()
    db.close()
import pytest
from fastapi.testclient import TestClient
from main import app
from auth import create_access_token

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_proyecto_data():
    return {
        "nombre": "Proyecto Test",
        "cliente": "Cliente Test",
        "descripcion": "Descripción de prueba",
        "fecha_inicio": "2025-09-13",
        "fecha_entrega": "2025-09-20",
        "estado": "pendiente"
    }

@pytest.fixture
def auth_headers():
    # Simula un usuario autenticado (ajusta según tu modelo de usuario)
    token = create_access_token({"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}
