from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0, le=1000000)
    stock: int = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=500)

    @validator('name')
    def validate_name(cls, v):
        if v.strip() != v:
            raise ValueError('El nombre no puede empezar o terminar con espacios')
        return v.title()

class ProductCreate(ProductBase):
    in_stock: bool = Field(True, description="Producto en stock")
    stock_quantity: int = Field(0, ge=0, le=9999, description="Cantidad en stock")
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    price: Optional[float] = Field(None, gt=0, le=1000000)
    stock: Optional[int] = Field(None, ge=0)

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryEnum(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    books = "books"
    home = "home"
    sports = "sports"

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    price: float = Field(..., gt=0, le=999999.99, description="Precio del producto")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del producto")
    category: CategoryEnum = Field(..., description="Categoría del producto")

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip().title()
        
class ProductList(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None