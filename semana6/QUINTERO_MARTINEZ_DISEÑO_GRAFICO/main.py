
# --- Endpoints de autenticación ---
from fastapi import Form, Body
from models import User
import hashlib

from fastapi import Body
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db, engine
from models import Base, Proyecto
from schemas import ProyectoCreate, ProyectoResponse
import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Diseño Gráfico")

@app.post("/auth/register", status_code=201)
def register_user(data: dict = Body(...), db: Session = Depends(get_db)):
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    if db.query(User).filter_by(username=username).first():
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    return {"message": "Usuario registrado"}

@app.post("/auth/login")
def login_user(data: dict = Body(...), db: Session = Depends(get_db)):
    username = data.get("username")
    password = data.get("password")
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user.hashed_password != hashed_password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    # Generar token JWT real
    from auth import create_access_token
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}


@app.put("/design_proyectos/{proyecto_id}", response_model=ProyectoResponse)
def update_proyecto(
    proyecto_id: int,
    proyecto_data: ProyectoCreate = Body(...),
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Actualizar campos
    proyecto.nombre = proyecto_data.nombre
    proyecto.cliente = proyecto_data.cliente
    proyecto.descripcion = proyecto_data.descripcion
    proyecto.fecha_inicio = proyecto_data.fecha_inicio
    proyecto.fecha_entrega = proyecto_data.fecha_entrega
    proyecto.estado = proyecto_data.estado
    db.commit()
    db.refresh(proyecto)
    return proyecto

@app.post("/design_proyectos/", response_model=ProyectoResponse, status_code=status.HTTP_201_CREATED)
def create_proyecto(
    proyecto_data: ProyectoCreate,
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):  
    """Crear nuevo proyecto de Diseño Gráfico"""
    # Validar duplicados por nombre y cliente
    existing = db.query(Proyecto).filter(
        Proyecto.nombre == proyecto_data.nombre,
        Proyecto.cliente == proyecto_data.cliente
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="El proyecto ya existe")

    proyecto = Proyecto(
        nombre=proyecto_data.nombre,
        cliente=proyecto_data.cliente,
        descripcion=proyecto_data.descripcion,
        fecha_inicio=proyecto_data.fecha_inicio,
        fecha_entrega=proyecto_data.fecha_entrega,
        estado=proyecto_data.estado
    )
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto


@app.get("/design_proyectos/", response_model=List[ProyectoResponse])
def list_proyectos(db: Session = Depends(get_db)):
    """Listar todos los proyectos"""
    return db.query(Proyecto).all()


@app.get("/design_proyectos/{proyecto_id}", response_model=ProyectoResponse)
def get_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    """Obtener proyecto por ID"""
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return proyecto


@app.delete("/design_proyectos/{proyecto_id}")
def delete_proyecto(proyecto_id: int, current_user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Eliminar un proyecto por ID (solo admin)"""
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    # Simulación de permisos: solo admin puede eliminar
    # En un sistema real, current_user debería tener un campo 'role'
    if getattr(current_user, "username", None) != "admin_design":
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar")
    db.delete(proyecto)
    db.commit()
    return {"message": "Proyecto eliminado exitosamente"}
