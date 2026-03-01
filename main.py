"""
Ecdotica — Sistema de evaluación editorial automatizada.
Editorial Nuevo Milenio

Uso:
    python main.py <ruta_manuscrito> <genero>

Géneros disponibles:
    novela, cuento, poema, ensayo, cronica

Ejemplo:
    python main.py manuscrito.txt novela
"""

import sys
import os

# Añadir el módulo de procesamiento al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'procesamiento'))

from evaluador import evaluar_manuscrito, reporte_resultados
from utils import analizar_manuscrito

GENEROS_DISPONIBLES = ['novela', 'cuento', 'poema', 'ensayo', 'cronica']


def main():
    if len(sys.argv) < 3:
        print("Uso: python main.py <ruta_manuscrito> <genero>")
        print(f"Géneros disponibles: {', '.join(GENEROS_DISPONIBLES)}")
        sys.exit(1)

    ruta = sys.argv[1]
    genero = sys.argv[2].lower()

    if not os.path.isfile(ruta):
        print(f"Error: No se encontró el archivo '{ruta}'")
        sys.exit(1)

    if genero not in GENEROS_DISPONIBLES:
        print(f"Error: Género '{genero}' no reconocido.")
        print(f"Géneros disponibles: {', '.join(GENEROS_DISPONIBLES)}")
        sys.exit(1)

    print(f"\nAnalizando manuscrito: {ruta}")
    print(f"Género: {genero}\n")

    stats = analizar_manuscrito(ruta)
    resultados = evaluar_manuscrito(stats, genero)
    print(reporte_resultados(resultados, genero))


if __name__ == '__main__':
    main()
