"""
Módulo de criterios editoriales para crónica.
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
    """Evalúa el rango de palabras de la crónica. Entre 500 y 15,000 palabras."""
    palabras = stats.get('num_palabras', 0)
    cumple = 500 <= palabras <= 15000
    if palabras < 500:
        mensaje = f'La crónica tiene {palabras} palabras. Mínimo requerido: 500'
    elif palabras > 15000:
        mensaje = f'La crónica tiene {palabras} palabras. Máximo recomendado: 15,000'
    else:
        mensaje = f'Longitud adecuada: {palabras} palabras'
    return {
        'cumple': cumple,
        'num_palabras': palabras,
        'mensaje': mensaje
    }


def evaluar_estructura(stats):
    """La crónica puede presentarse como texto continuo sin capítulos."""
    return {
        'cumple': True,
        'mensaje': 'La crónica no requiere estructura de capítulos'
    }


def evaluar_legibilidad(stats):
    """Evalúa el índice de legibilidad. Mínimo recomendado: 55 (estilo periodístico, accesible)."""
    indice = stats.get('indice_legibilidad', 100)
    cumple = indice >= 55
    mensaje = f'Índice de legibilidad: {indice:.2f}. Mínimo recomendado: 55'
    return {
        'cumple': cumple,
        'indice': indice,
        'mensaje': mensaje
    }


def evaluar_cronica(stats):
    """Evalúa todos los criterios y devuelve dict con resultados detallados."""
    return {
        'ortografia_gramatica': evaluar_ortografia_gramatica(stats),
        'longitud': evaluar_longitud(stats),
        'estructura': evaluar_estructura(stats),
        'legibilidad': evaluar_legibilidad(stats)
    }
