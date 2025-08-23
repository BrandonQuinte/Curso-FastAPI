# schemas.py
from pydantic import BaseModel, validator
from typing import List, Optional

# Schemas para Categoría
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: str

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int

    class Config:
        from_attributes = True

# Schemas actualizados para Producto
class ProductoBase(BaseModel):
    nombre: str
    precio: float
    descripcion: str
    categoria_id: Optional[int] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: str = None
    precio: float = None
    descripcion: str = None
    categoria_id: int = None

# Producto con información de categoría incluida
class ProductoConCategoria(ProductoBase):
    id: int
    categoria: Optional[Categoria] = None

    class Config:
        from_attributes = True

# Categoría con lista de productos
class CategoriaConProductos(Categoria):
    productos: List[ProductoBase] = []

    class Config:
        from_attributes = True
class AutorBase(BaseModel):
    nombre: str
    nacionalidad: str

class AutorCreate(AutorBase):
    pass

class Autor(AutorBase):
    id: int

    class Config:
        from_attributes = True

class LibroBase(BaseModel):
    titulo: str
    precio: float
    paginas: int
    autor_id: Optional[int] = None

class LibroCreate(LibroBase):
    pass

class LibroConAutor(LibroBase):
    id: int
    autor: Optional[Autor] = None

    class Config:
        from_attributes = True

class AutorConLibros(Autor):
    libros: List[LibroBase] = []

    class Config:
        from_attributes = True
        
class LibroBase(BaseModel):
    titulo: str
    precio: float
    paginas: int
    autor_id: Optional[int] = None

    @validator('precio')
    def validar_precio(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return v

    @validator('paginas')
    def validar_paginas(cls, v):
        if v <= 0:
            raise ValueError('El número de páginas debe ser mayor a 0')
        return v

    @validator('titulo')
    def validar_titulo(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('El título no puede estar vacío')
        return v.strip()        