#!/bin/bash
echo "í¾¨ Formateando cÃ³digo con Black..."
black app/ tests/

echo "í³¦ Organizando imports con isort..."
isort app/ tests/

echo "âœ… Formateo completado"

