#!/bin/bash
echo "Ì¥ç Ejecutando flake8..."
flake8 app/ tests/

echo "Ì¥í Ejecutando bandit (seguridad)..."
bandit -r app/

echo "Ìø∑Ô∏è  Ejecutando mypy (tipos)..."
mypy app/

echo "‚úÖ Linting completado"

