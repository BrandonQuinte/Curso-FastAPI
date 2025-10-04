"""Descripciones centralizadas para la documentación API - Tipo D (Inmobiliaria Premium RealEstate)"""

# Descripciones de tags
TAGS_METADATA = [
    {
        "name": "usuarios",
        "description": "Operaciones CRUD para gestionar usuarios del sistema Tipo D. "
        "Incluye administración de roles, acceso y estado de actividad.",
        "externalDocs": {
            "description": "Documentación externa de gestión de usuarios",
            "url": "https://docs.realestatepremium.com/api-usuarios",
        },
    },
    {
        "name": "agentes",
        "description": "Endpoints relacionados con la gestión de agentes inmobiliarios y su información profesional.",
    },
    {
        "name": "propiedades",
        "description": "Operaciones CRUD para el catálogo de propiedades de la inmobiliaria.",
    },
    {
        "name": "reportes",
        "description": "Generación de reportes de desempeño, actividad y estado de los usuarios/agentes.",
    },
]

# Descripciones de endpoints
ENDPOINT_DESCRIPTIONS = {
    "crear_usuario": """
    ### Crear Nuevo Usuario (Tipo D)

    Crea un nuevo usuario dentro del sistema **RealEstate Premium**.  
    Los usuarios pueden tener distintos **niveles de acceso** dependiendo de su rol: `admin`, `editor` o `lector`.

    #### Ejemplo de uso:
    ```json
    {
        "username": "usuario_demo",
        "email": "demo@correo.com",
        "password": "segura123",
        "rol": "editor"
    }
    ```

    #### Validaciones:
    - El `username` debe ser único.
    - El `email` debe tener formato válido.
    - La contraseña debe tener mínimo 6 caracteres.
    """,
    "obtener_usuario": """
    ### Obtener Usuario por ID

    Recupera un usuario específico usando su identificador único.

    #### Respuesta exitosa:
    - Retorna toda la información del usuario.
    - Incluye fechas de creación y última conexión.
    - Muestra estado activo/inactivo y rol asignado.

    #### Casos de error:
    - **404**: Usuario no encontrado.
    - **422**: ID inválido.
    """,
    "listar_usuarios": """
    ### Listar Usuarios con Paginación

    Obtiene una lista paginada de usuarios tipo D.

    #### Parámetros de filtrado:
    - **rol**: Filtra por rol (`admin`, `editor`, `lector`).
    - **activo**: Filtra por estado activo/inactivo.
    - **buscar**: Búsqueda por nombre o correo.

    #### Paginación:
    - **pagina**: Número de página (default: 1)
    - **limite**: Elementos por página (default: 10, max: 50)

    #### Ordenamiento:
    - **orden_por**: Campo para ordenar (`username`, `fecha_creacion`, `rol`)
    - **direccion**: asc (ascendente) o desc (descendente)
    """,
    "actualizar_usuario": """
    ### Actualizar Usuario Existente

    Actualiza parcialmente los datos de un usuario.  
    Solo los campos enviados serán modificados.

    #### Campos actualizables:
    - `email`, `rol`, `activo`

    #### Validaciones:
    - El `email` debe tener formato válido.
    - El `rol` debe ser uno de los valores válidos (`admin`, `editor`, `lector`).
    """,
    "eliminar_usuario": """
    ### Eliminar Usuario

    Elimina un usuario permanentemente del sistema.

    ⚠️ **Advertencia**: Esta acción no puede deshacerse.

    #### Validaciones:
    - El usuario debe existir.
    - No debe tener registros dependientes (ej. propiedades asignadas).
    """,
}

# Descripciones de respuestas comunes
RESPONSE_DESCRIPTIONS = {
    200: "Operación exitosa",
    201: "Usuario creado exitosamente",
    204: "Usuario eliminado exitosamente",
    400: "Solicitud inválida - Error en los datos enviados",
    404: "Usuario no encontrado",
    422: "Error de validación - Datos no cumplen con los esquemas",
    500: "Error interno del servidor",
}

# Ejemplos de responses
RESPONSE_EXAMPLES = {
    "usuario_creado": {
        "summary": "Usuario creado exitosamente",
        "description": "Ejemplo de respuesta cuando se crea un nuevo usuario tipo D",
        "value": {
            "id": 10,
            "username": "usuario_demo",
            "email": "demo@correo.com",
            "rol": "editor",
            "activo": True,
            "fecha_creacion": "2025-01-10T09:00:00",
            "ultima_conexion": None,
        },
    },
    "lista_usuarios": {
        "summary": "Lista de usuarios paginada",
        "description": "Ejemplo de respuesta con lista paginada de usuarios",
        "value": {
            "usuarios": [
                {
                    "id": 1,
                    "username": "admin_user",
                    "email": "admin@correo.com",
                    "rol": "admin",
                    "activo": True,
                },
                {
                    "id": 2,
                    "username": "editor_user",
                    "email": "editor@correo.com",
                    "rol": "editor",
                    "activo": True,
                },
            ],
            "total": 2,
            "pagina": 1,
            "por_pagina": 10,
        },
    },
    "error_no_encontrado": {
        "summary": "Usuario no encontrado",
        "description": "Error cuando se busca un usuario inexistente",
        "value": {
            "error": "USUARIO_NO_ENCONTRADO",
            "mensaje": "El usuario con ID 999 no fue encontrado",
            "codigo_http": 404,
            "timestamp": "2025-01-10T09:00:00",
        },
    },
    "error_validacion": {
        "summary": "Error de validación",
        "description": "Error cuando los datos no cumplen las validaciones requeridas",
        "value": {
            "error": "VALIDACION_FALLIDA",
            "mensaje": "El email debe tener formato válido",
            "codigo_http": 422,
            "timestamp": "2025-01-10T09:00:00",
        },
    },
}
