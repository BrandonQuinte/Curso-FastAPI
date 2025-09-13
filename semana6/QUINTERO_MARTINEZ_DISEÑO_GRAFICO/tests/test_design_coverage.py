import pytest
import uuid

def test_critical_paths_diseno_grafico(client, auth_headers):
    """
    Test de rutas críticas para Diseño Gráfico
    """
    # Usar username fijo 'admin_design'
    register_data = {
        "username": "admin_design",
        "password": "admin123",
        "role": "admin"
    }
    # Intentar registrar, si ya existe ignorar el error
    reg_resp = client.post("/auth/register", json=register_data)
    if reg_resp.status_code not in (201, 400):
        assert False, f"Error inesperado al registrar: {reg_resp.text}"

    # Login siempre
    login_resp = client.post("/auth/login", json={"username": "admin_design", "password": "admin123"})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    proyecto_data = {
        "nombre": f"Identidad Visual Rockfest {uuid.uuid4().hex}",
        "cliente": f"Eventos Bogotá {uuid.uuid4().hex}",
        "descripcion": "Diseño de marca, logo y piezas digitales para festival musical.",
        "fecha_inicio": "2025-09-15",
        "fecha_entrega": "2025-09-30",
        "estado": "en_progreso"
    }
    crear = client.post("/design_proyectos/", json=proyecto_data, headers=headers)
    if crear.status_code != 201:
        print("Error al crear proyecto:", crear.text)
    assert crear.status_code == 201, f"Fallo al crear proyecto: {crear.text}"
    proyecto_id = crear.json()["id"]

    consultar = client.get(f"/design_proyectos/{proyecto_id}", headers=headers)
    assert consultar.status_code == 200, f"Fallo al consultar proyecto por ID: {consultar.text}"
    assert consultar.json()["nombre"] == proyecto_data["nombre"]

    eliminar = client.delete(f"/design_proyectos/{proyecto_id}", headers=headers)
    assert eliminar.status_code == 200, f"Fallo al eliminar proyecto: {eliminar.text}"

    verificar = client.get(f"/design_proyectos/{proyecto_id}", headers=headers)
    assert verificar.status_code == 404, f"El proyecto eliminado aún está disponible: {verificar.text}"