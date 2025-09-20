# app/database/optimized_queries.py
from typing import Dict

class DomainOptimizedQueries:
    """Consultas optimizadas específicas para el dominio Academia Idiomas"""

    @staticmethod
    def get_academia_idiomas_queries() -> Dict[str, str]:
        """
        Consultas optimizadas para la Academia de Idiomas (dominio lang_)
        Foco en: cursos, niveles, grupos, profesores y estudiantes.
        """
        return {
            # Catálogo de cursos por nivel y estado
            "cursos_por_nivel": """
                SELECT c.id, c.nombre, c.nivel, c.estado, c.duracion, p.nombre as profesor
                FROM lang_curso c
                LEFT JOIN profesores p ON c.profesor_id = p.id
                WHERE c.nivel = :nivel
                AND (:estado IS NULL OR c.estado = :estado)
                ORDER BY c.nombre
                LIMIT :limit OFFSET :offset
            """,

            # Estudiantes inscritos en un curso específico
            "inscripciones_por_curso": """
                SELECT i.id, e.nombre, e.apellido, i.fecha_inscripcion, i.estado
                FROM lang_inscripcion i
                JOIN estudiantes e ON i.estudiante_id = e.id
                WHERE i.curso_id = :curso_id
                ORDER BY i.fecha_inscripcion DESC
                LIMIT :limit OFFSET :offset
            """,

            # Grupos de un curso (ej. curso de inglés nivel B1 con varios grupos)
            "grupos_por_curso": """
                SELECT g.id, g.nombre, g.horario, g.capacidad, COUNT(i.id) as inscritos
                FROM lang_grupo g
                LEFT JOIN lang_inscripcion i ON g.id = i.grupo_id
                WHERE g.curso_id = :curso_id
                GROUP BY g.id
                ORDER BY g.nombre
            """,

            # Próximos cursos que empiezan en los siguientes 30 días
            "proximos_cursos": """
                SELECT c.id, c.nombre, c.nivel, c.fecha_inicio, p.nombre as profesor
                FROM lang_curso c
                LEFT JOIN profesores p ON c.profesor_id = p.id
                WHERE c.fecha_inicio BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
                ORDER BY c.fecha_inicio ASC
            """,

            # Cursos por profesor
            "cursos_por_profesor": """
                SELECT c.id, c.nombre, c.nivel, c.estado, COUNT(i.id) as total_inscritos
                FROM lang_curso c
                LEFT JOIN lang_inscripcion i ON c.id = i.curso_id
                WHERE c.profesor_id = :profesor_id
                GROUP BY c.id
                ORDER BY c.nombre
            """
        }

    @staticmethod
    def get_queries_for_domain(domain_prefix: str) -> Dict[str, str]:
        """
        Obtiene las consultas optimizadas según el dominio.
        Para Academia Idiomas (prefijo lang_) usamos las consultas adaptadas.
        """
        if domain_prefix.startswith("lang_"):
            return DomainOptimizedQueries.get_academia_idiomas_queries()
        return {}
