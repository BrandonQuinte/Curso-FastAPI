# Guía de Contribución - Dominio Tipo D

## Proceso de Desarrollo

1. **Crear rama feature**: `git checkout -b feature/nueva-funcionalidad`
2. **Desarrollar**: Implementar cambios siguiendo estándares
3. **Calidad**: Ejecutar `./scripts/quality.sh`
4. **Tests**: Asegurar cobertura > 80%
5. **Commit**: Usar conventional commits
6. **Push**: `git push origin feature/nueva-funcionalidad`
7. **PR**: Crear Pull Request con descripción detallada

## Estándares de Código

- **Formateo**: Black con líneas de 88 caracteres  
- **Imports**: isort con perfil black  
- **Linting**: flake8 con configuración del proyecto  
- **Tipos**: mypy para verificación estática  
- **Seguridad**: bandit para análisis de vulnerabilidades  
- **Tests**: pytest con cobertura mínima 80%
