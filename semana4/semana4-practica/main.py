from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine, get_db

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Productos con Categorías")

# ENDPOINTS PARA CATEGORÍAS

@app.post("/categorias/", response_model=schemas.Categoria)
def crear_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    return crud.crear_categoria(db=db, categoria=categoria)

@app.get("/categorias/", response_model=list[schemas.Categoria])
def listar_categorias(db: Session = Depends(get_db)):
    return crud.obtener_categorias(db)

@app.get("/categorias/{categoria_id}", response_model=schemas.CategoriaConProductos)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = crud.obtener_categoria_con_productos(db, categoria_id=categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

# ENDPOINTS ACTUALIZADOS PARA PRODUCTOS

@app.get("/productos/", response_model=list[schemas.ProductoConCategoria])
def listar_productos_con_categoria(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return crud.obtener_productos_con_categoria(db, skip=skip, limit=limit)

@app.get("/categorias/{categoria_id}/productos/", response_model=list[schemas.ProductoConCategoria])
def productos_por_categoria(categoria_id: int, db: Session = Depends(get_db)):
    productos = crud.obtener_productos_por_categoria(db, categoria_id=categoria_id)
    return productos

# CREATE - Crear producto con validaciones
@app.post("/productos/", response_model=schemas.ProductoConCategoria)
def crear_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    try:
        return crud.crear_producto(db=db, producto=producto)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# READ - Obtener producto por ID
@app.get("/productos/{producto_id}", response_model=schemas.ProductoConCategoria)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = crud.obtener_producto(db, producto_id=producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# UPDATE - Actualizar producto parcialmente
@app.patch("/productos/{producto_id}", response_model=schemas.ProductoConCategoria)
def actualizar_producto(
    producto_id: int,
    producto: schemas.ProductoUpdate,
    db: Session = Depends(get_db)
):
    db_producto = crud.actualizar_producto(db, producto_id=producto_id, producto=producto)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto

# DELETE - Eliminar producto
@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = crud.eliminar_producto(db, producto_id=producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": f"Producto {producto_id} eliminado correctamente"}

# STATS - Estadísticas básicas
@app.get("/productos/stats/resumen")
def estadisticas_productos(db: Session = Depends(get_db)):
    total = crud.contar_productos(db)
    productos = crud.obtener_productos(db, limit=total)

    if not productos:
        return {"total": 0, "precio_promedio": 0, "precio_max": 0, "precio_min": 0}

    precios = [p.precio for p in productos]  # Ajustado a 'precio' según tu modelo
    return {
        "total": total,
        "precio_promedio": sum(precios) / len(precios),
        "precio_max": max(precios),
        "precio_min": min(precios)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

