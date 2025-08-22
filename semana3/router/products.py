from fastapi import APIRouter, HTTPException, Query, Path, status
from typing import Optional
from models.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductList, CategoryEnum
)
from services.product_service import (
    get_product_by_id, create_product,
    update_product, delete_product, filter_products
)

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/",
    response_model=ProductList,
    summary="Obtener lista de productos"
)
async def get_products(
    category: Optional[CategoryEnum] = Query(None),
    in_stock: Optional[bool] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=1)
):
    products_filtered = filter_products(
        category=category.value if category else None,
        in_stock=in_stock,
        min_price=min_price,
        max_price=max_price
    )
    if search:
        search_lower = search.lower()
        products_filtered = [
            p for p in products_filtered
            if search_lower in p["name"].lower() or
               (p.get("description") and search_lower in p["description"].lower())
        ]
    total = len(products_filtered)
    start = (page - 1) * page_size
    end = start + page_size
    return ProductList(
        products=products_filtered[start:end],
        total=total,
        page=page,
        page_size=page_size
    )

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Obtener producto por ID"
)
async def get_product(product_id: int = Path(..., gt=0)):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    return ProductResponse(**product)

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo producto"
)
async def create_new_product(product: ProductCreate):
    new_product = create_product(product)
    if not new_product:
        raise HTTPException(
            status_code=409,
            detail=f"Producto '{product.name}' ya existe"
        )
    return ProductResponse(**new_product)

@router.delete(
    "/{product_id}",
    summary="Eliminar producto"
)
async def delete_product_endpoint(product_id: int):
    deleted = delete_product(product_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"No existe producto con ID {product_id}"
        )
    return {"success":True,"deleted_product": deleted}