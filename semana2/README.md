# Mi API FastAPI - Semana 2

## ¿Qué hace?

API mejorada con validación automática de datos y type hints.

## Nuevos Features (Semana 2)

- ✅ Type hints en todas las funciones
- ✅ Validación automática con Pydantic
- ✅ Endpoint POST para crear datos
- ✅ Parámetros de ruta (ejemplo: /products/{id})
- ✅ Búsqueda con parámetros query

## ¿Cómo ejecutar?

```bash
pip install fastapi pydantic uvicorn
uvicorn main:app --reload
```

## ¿Los type hints hacen tu código más claro? ¿Por qué?

Claro que si porque cuando se usan type hints, se dice especificamente que tipo de datos esperamos en cada parámetro y qué será lo que devolverá la funcion que vayamosa utilizar. Se muestran los tipos esperados y ademas explica si un parametro es obligatorio u opcional.

![Evidencia-type-hints](image.png)


## ¿Cómo te ayuda Pydantic a crear APIs más robustas?

Cuando se utiliza Pydantic, el POST se ve mas ordenado con cada campo que tiene un tipo de variable y reglas que cumplir o si no de lo contrario nos dará un error de campo, además podemos crear mas APIs sin límite mientras se cumplen las reglas de variable.

![Evidencia-Pydantic](image.png)


## ¿Cómo mejoraron estos conceptos tu API comparada con Semana 1?

Conocer y aprender más de ellos ayudan mucho a tenerle mayor lógica a las cosas, el modelado de datos con el tipo de campo o de variable que se necesita para poner un producto o algo, modelos Pydantic más específicos para respetar las reglas de variables, parámetros de Query y Responses ideales para hacer las búsquedas mas específicas y tambien con ciertos mensajes que a uno le ponen si se cumple con las reglas o no.

![Evidencia-POST](image.png)

