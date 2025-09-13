import uuid

def test_register_design_user(client):
    """Test de registro específico para Diseño Gráfico"""
    unique_username = f"usuario_design_test_{uuid.uuid4().hex}"
    data = {
        "username": unique_username,
        "password": "password123",
        "role": "designer"  # Usar el rol correcto según la lógica del backend
    }
    response = client.post("/auth/register", json=data)
    assert response.status_code == 201


def test_login_design_user(client):
    """Test de login específico para Diseño Gráfico"""
    # Registrar usuario admin único
    unique_admin = f"admin_design_{uuid.uuid4().hex}"
    register_data = {
        "username": unique_admin,
        "password": "admin123",
        "role": "admin"
    }
    reg_resp = client.post("/auth/register", json=register_data)
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"

    # Login
    login_data = {
        "username": unique_admin,
        "password": "admin123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    assert "access_token" in response.json()


def test_designer_permissions(client):
    """Test de permisos específicos para diseñador"""
    # Registrar usuario diseñador único
    designer_username = f"designer_{uuid.uuid4().hex}"
    register_data = {
        "username": designer_username,
        "password": "designer123",
        "role": "designer"
    }
    reg_resp = client.post("/auth/register", json=register_data)
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"
    login_resp = client.post("/auth/login", json={"username": designer_username, "password": "designer123"})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "nombre": f"Proyecto permiso diseño {uuid.uuid4().hex}",
        "cliente": f"Cliente Test {uuid.uuid4().hex}",
        "descripcion": "Test permisos de diseño",
        "fecha_inicio": "2025-09-10",
        "fecha_entrega": "2025-09-20",
        "estado": "en_progreso"
    }
    response = client.post("/design_proyectos/", json=data, headers=headers)
    assert response.status_code == 201, f"Project creation failed: {response.text}"
    proyecto_id = response.json()["id"]
    delete_response = client.delete(f"/design_proyectos/{proyecto_id}", headers=headers)
    assert delete_response.status_code in (403, 401), f"Designer should not delete: {delete_response.text}"


def test_create_proyecto_requires_auth(client):
    """Test que crear proyecto requiere autenticación"""
    data = {
        "nombre": "Proyecto sin auth",
        "cliente": "Cliente X",
        "descripcion": "Debe fallar",
        "fecha_inicio": "2025-09-10",
        "fecha_entrega": "2025-09-20",
        "estado": "en_progreso"
    }

    response = client.post("/design_proyectos/", json=data)
    assert response.status_code in (401, 403)


def test_admin_can_delete_proyecto(client):
    """Test que solo admin puede eliminar proyectos"""
    # Usar username fijo 'admin_design' para que el backend permita eliminar
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

    data = {
        "nombre": f"Proyecto para borrar {uuid.uuid4().hex}",
        "cliente": f"Cliente Admin {uuid.uuid4().hex}",
        "descripcion": "Test delete admin",
        "fecha_inicio": "2025-09-10",
        "fecha_entrega": "2025-09-20",
        "estado": "en_progreso"
    }
    create_resp = client.post("/design_proyectos/", json=data, headers=headers)
    assert create_resp.status_code == 201, f"Project creation failed: {create_resp.text}"
    proyecto_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/design_proyectos/{proyecto_id}", headers=headers)
    assert delete_resp.status_code == 200, f"Admin delete failed: {delete_resp.text}"


def test_regular_user_cannot_delete_proyecto(client):
    """Test que usuario regular no puede eliminar proyectos"""
    user_username = f"user_design_{uuid.uuid4().hex}"
    register_data = {
        "username": user_username,
        "password": "user123",
        "role": "designer"
    }
    reg_resp = client.post("/auth/register", json=register_data)
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"
    login_resp = client.post("/auth/login", json={"username": user_username, "password": "user123"})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "nombre": f"Proyecto no borrable {uuid.uuid4().hex}",
        "cliente": f"Cliente User {uuid.uuid4().hex}",
        "descripcion": "Test delete user",
        "fecha_inicio": "2025-09-10",
        "fecha_entrega": "2025-09-20",
        "estado": "en_progreso"
    }
    create_resp = client.post("/design_proyectos/", json=data, headers=headers)
    assert create_resp.status_code == 201, f"Project creation failed: {create_resp.text}"
    proyecto_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/design_proyectos/{proyecto_id}", headers=headers)
    assert delete_resp.status_code in (403, 401), f"Regular user should not delete: {delete_resp.text}"
