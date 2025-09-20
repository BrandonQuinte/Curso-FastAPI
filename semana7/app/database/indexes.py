# app/database/indexes.py
from sqlalchemy import text
from app.database import engine

class DomainIndexes:
    """Índices específicos para optimizar consultas de Academia Idiomas"""

    @staticmethod
    def create_academia_idiomas_indexes():
        """
        Índices optimizados para el dominio Academia Idiomas.
        Foco en: curso (entidad principal), niveles y grupos.
        """
        indexes = [
            # Búsquedas frecuentes de cursos por nivel y estado
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lang_curso_nivel_estado "
            "ON lang_curso(nivel, estado);",

            # Consultas por grupo y curso
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lang_grupo_curso "
            "ON lang_grupo(curso_id, nombre);",

            # Consultas de catálogo de cursos (nombre, duración)
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lang_curso_nombre_duracion "
            "ON lang_curso(nombre, duracion);",

            # Consultas frecuentes de inscripciones por curso y estudiante
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lang_inscripcion_curso_estudiante "
            "ON lang_inscripcion(curso_id, estudiante_id, fecha_inscripcion DESC);",

            # Búsquedas por profesor asignado
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lang_curso_profesor "
            "ON lang_curso(profesor_id, nivel);",
        ]
        return indexes

    @staticmethod
    def get_domain_indexes(domain_prefix: str):
        """
        Obtiene índices según el dominio.
        Para Academia Idiomas (lang_), usamos índices optimizados de cursos, niveles y grupos.
        """
        if domain_prefix.startswith("lang_"):
            return DomainIndexes.create_academia_idiomas_indexes()
        else:
            # Índices genéricos si el dominio no es reconocido
            return [
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_entidad_principal_usuario "
                "ON entidad_principal(usuario_id, fecha_creacion DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_entidad_principal_estado "
                "ON entidad_principal(estado, fecha_actualizacion);",
            ]

    @staticmethod
    async def create_indexes_for_domain(domain_prefix: str = "lang_"):
        """Crea índices específicos para el dominio Academia Idiomas"""
        indexes = DomainIndexes.get_domain_indexes(domain_prefix)

        with engine.connect() as connection:
            for index_sql in indexes:
                try:
                    connection.execute(text(index_sql))
                    print(f"✅ Índice creado: {index_sql[:60]}...")
                except Exception as e:
                    print(f"❌ Error creando índice: {e}")
