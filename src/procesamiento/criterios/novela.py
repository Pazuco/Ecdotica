"""
Módulo de criterios editoriales para novela.
Editorial Nuevo Milenio
"""

def evaluar_ortografia_gramatica(stats):
      """Evalúa ortografía y gramática. Se espera menos de 10 errores graves por cada 10,000 palabras."""
      errores_graves = stats.get('errores_graves', 0)
      palabras = stats.get('num_palabras', 1)
      tasa_error = errores_graves / palabras * 10000
      return {
          'cumple': tasa_error < 10,
          'tasa_error': tasa_error,
          'mensaje': f'Tasa de errores: {tasa_error:.2f} por 10,000 palabras'
      }


def evaluar_longitud(stats):
      """Evalúa el rango de palabras de la novela. Entre 30,000 y 150,000 palabras."""
      palabras = stats.get('num_palabras', 0)
      cumple = 30000 <= palabras <= 150000
      if palabras < 30000:
                mensaje = f'La novela tiene {palabras} palabras. Mínimo requerido: 30,000'
            elif palabras > 150000:
                      mensaje = f'La novela tiene {palabras} palabras. Máximo recomendado: 150,000'
                  else:
        mensaje = f'Longitud adecuada: {palabras} palabras'
                        return {
                            'cumple': cumple,
                            'num_palabras': palabras,
                            'mensaje': mensaje
                        }


                    def evaluar_estructura(stats):
                          """Evalúa si la novela tiene capítulos. Se requieren al menos 3 capítulos."""
                          num_capitulos = stats.get('num_capitulos', 0)
                          cumple = num_capitulos >= 3
                          mensaje = f'Capítulos detectados: {num_capitulos}. Mínimo requerido: 3'
                          return {
                              'cumple': cumple,
                              'num_capitulos': num_capitulos,
                              'mensaje': mensaje
                          }


                    def evaluar_legibilidad(stats):
                          """Evalúa el índice de legibilidad. Debe ser al menos 50."""
                          indice = stats.get('indice_legibilidad', 100)
                          cumple = indice >= 50
                          mensaje = f'Índice de legibilidad: {indice:.2f}. Mínimo recomendado: 50'
                          return {
                              'cumple': cumple,
                              'indice': indice,
                              'mensaje': mensaje
                          }


                    def evaluar_novela(stats):
                          """Evalúa todos los criterios y devuelve dict con resultados detallados."""
                          return {
                              'ortografia_gramatica': evaluar_ortografia_gramatica(stats),
                              'longitud': evaluar_longitud(stats),
                              'estructura': evaluar_estructura(stats),
                              'legibilidad': evaluar_legibilidad(stats)
                          }
