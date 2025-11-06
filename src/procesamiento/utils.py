"""
Funciones utilitarias para análisis de textos.
Editorial Nuevo Milenio
"""

import re

def contar_palabras(texto):
      """Cuenta el número total de palabras en el texto."""
      return len(re.findall(r'\w+', texto))

def contar_capitulos(texto):
      """Busca la palabra 'Capítulo' al inicio de línea (cualquier variación)."""
      return len(re.findall(r'(?mi)^cap[\u00ed]tulo', texto))

def calcular_legibilidad(texto):
      """Fórmula simple para español (puede mejorarse con SpaCy o herramientas especializadas)."""
      palabras = contar_palabras(texto)
      oraciones = len(re.findall(r'[.!?]', texto))
      if palabras == 0 or oraciones == 0:
                return 100
            return max(0, min(100, 206.835 - 1.015 * (palabras / oraciones) - 84.6 * (len(texto) / palabras)))

def detectar_errores(texto):
      """Función de ejemplo que simula 5 errores. Integrar LanguageTool o corrector real aquí."""
    return 5

def analizar_manuscrito(path):
      """Lee un archivo .txt y extrae estadísticas de análisis."""
    with open(path, encoding='utf-8') as f:
              texto = f.read()
          stats = {
                    'num_palabras': contar_palabras(texto),
                    'num_capitulos': contar_capitulos(texto),
                    'indice_legibilidad': calcular_legibilidad(texto),
                    'errores_graves': detectar_errores(texto),
                }
    return stats
