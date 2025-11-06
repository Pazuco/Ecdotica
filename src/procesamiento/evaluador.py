"""
Pipeline central para evaluación editorial automatizada.
Editorial Nuevo Milenio
"""

from criterios import novela, cuento
from utils import analizar_manuscrito

GENERO_CRITERIOS = {
      'novela': novela.evaluar_novela,
      'cuento': cuento.evaluar_cuento,
  }

def evaluar_manuscrito(stats, genero):
      """Evalúa un manuscrito según el género especificado."""
      if genero not in GENERO_CRITERIOS:
                raise ValueError(f'Género no implementado: {genero}')
            resultados = GENERO_CRITERIOS[genero](stats)
    return resultados

def reporte_resultados(resultados, genero):
      """Genera un reporte de evaluación."""
    mensajes = []
    for criterio, valor in resultados.items():
              cumple = valor.get('cumple', False)
              mensaje = valor.get('mensaje', f'{criterio}: sin información')
              estado = '✓' if cumple else '✗'
              mensajes.append(f'{estado} {mensaje}')
          apto = all([v.get('cumple', False) for v in resultados.values()])
    mensajes.append('---')
    if apto:
              mensajes.append(f'APTO para publicación en {genero.upper()}')
          else:
        mensajes.append(f'NO APTO para publicación en {genero.upper()}')
                return '\n'.join(mensajes)

if __name__ == '__main__':
      import sys
    if len(sys.argv) < 3:
              print('Uso: python evaluador.py <ruta_manuscrito> <genero>')
              sys.exit(1)
          ruta = sys.argv[1]
    genero = sys.argv[2]
    stats = analizar_manuscrito(ruta)
    resultados = evaluar_manuscrito(stats, genero)
    print(reporte_resultados(resultados, genero))
