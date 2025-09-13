from pydantic import BaseModel, Field
from typing import Optional

class ProyectoCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    cliente: str
    descripcion: Optional[str] = None
    fecha_inicio: Optional[str] = None  
    fecha_entrega: Optional[str] = None
    estado: Optional[str] = "pendiente"  

class ProyectoResponse(BaseModel):
    id: int
    nombre: str
    cliente: str
    descripcion: Optional[str]
    fecha_inicio: Optional[str]
    fecha_entrega: Optional[str]
    estado: Optional[str]

    class Config:
        orm_mode = True  
