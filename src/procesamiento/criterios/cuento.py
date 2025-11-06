"""
Módulo de criterios editoriales para cuento.
Editorial Nuevo Milenio
"""

def evaluar_ortografia_gramatica(stats):
      """Evalúa ortografía y gramática. Se espera menos de 5 errores graves por cada 5,000 palabras."""
      errores_graves = stats.get('errores_graves', 0)
      palabras = stats.get('num_palabras', 1)
      tasa_error = errores_graves / palabras * 5000
      return {
          'cumple': tasa_error < 5,
          'tasa_error': tasa_error,
          'mensaje': f'Tasa de errores: {tasa_error:.2f} por 5,000 palabras'
      }


def evaluar_longitud(stats):
      """Evalúa el rango de palabras del cuento. Entre 1,000 y 30,000 palabras."""
      palabras = stats.get('num_palabras', 0)
      cumple = 1000 <= palabras <= 30000
      if palabras < 1000:
                mensaje = f'El cuento tiene {palabras} palabras. Mínimo requerido: 1,000'
            elif palabras > 30000:
                      mensaje = f'El cuento tiene {palabras} palabras. Máximo recomendado: 30,000'
                  else:
        mensaje = f'Longitud adecuada: {palabras} palabras'
                        return {
                            'cumple': cumple,
                            'num_palabras': palabras,
                            'mensaje': mensaje
                        }


                    def evaluar_estructura(stats):
                          """El cuento puede ser texto único, no requiere capítulos obligatoriamente."""
                          return {
                              'cumple': True,
                              'mensaje': 'El cuento no requiere estructura de capítulos'
                          }


                    def evaluar_legibilidad(stats):
                          """Evalúa el índice de legibilidad. Debe ser al menos 60."""
                          indice = stats.get('indice_legibilidad', 100)
                          cumple = indice >= 60
                          mensaje = f'Índice de legibilidad: {indice:.2f}. Mínimo recomendado: 60'
                          return {
                              'cumple': cumple,
                              'indice': indice,
                              'mensaje': mensaje
                          }


                    def evaluar_cuento(stats):
                          """Evalúa todos los criterios y devuelve dict con resultados detallados."""
                          return {
                              'ortografia_gramatica': evaluar_ortografia_gramatica(stats),
                              'longitud': evaluar_longitud(stats),
                              'estructura': evaluar_estructura(stats),
                              'legibilidad': evaluar_legibilidad(stats)
                          }
