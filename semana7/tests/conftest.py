import sys
import os

# Agrega la ruta del directorio 'semana7' al sys.path si no está
current_dir = os.path.dirname(os.path.abspath(__file__))
semana7_dir = os.path.abspath(os.path.join(current_dir, '..'))
if semana7_dir not in sys.path:
    sys.path.insert(0, semana7_dir)
