#!/bin/bash
echo "íº€ Ejecutando revisiÃ³n completa de calidad..."

# Formateo
./scripts/format.sh

# Linting
./scripts/lint.sh

# Tests
echo "í·ª Ejecutando tests..."
pytest tests/ -v --cov=app --cov-report=html

echo "âœ… RevisiÃ³n de calidad completada"

