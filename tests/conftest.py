"""
Configuración de pytest para el proyecto Ecdotica.
Añade el módulo de procesamiento al path para que los tests puedan importar sus módulos.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'procesamiento'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
