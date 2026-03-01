"""
Módulo de criterios editoriales para poema.
Editorial Nuevo Milenio
"""


def evaluar_ortografia_gramatica(stats):
    """Evalúa ortografía y gramática. Se espera menos de 5 errores graves por cada 1,000 palabras."""
    errores_graves = stats.get('errores_graves', 0)
    palabras = stats.get('num_palabras', 1)
    tasa_error = errores_graves / palabras * 1000
    return {
        'cumple': tasa_error < 5,
        'tasa_error': tasa_error,
        'mensaje': f'Tasa de errores: {tasa_error:.2f} por 1,000 palabras'
    }


def evaluar_longitud(stats):
    """Evalúa el rango de palabras del poema. Entre 5 y 2,000 palabras."""
    palabras = stats.get('num_palabras', 0)
    cumple = 5 <= palabras <= 2000
    if palabras < 5:
        mensaje = f'El poema tiene {palabras} palabras. Mínimo requerido: 5'
    elif palabras > 2000:
        mensaje = f'El poema tiene {palabras} palabras. Máximo recomendado: 2,000'
    else:
        mensaje = f'Longitud adecuada: {palabras} palabras'
    return {
        'cumple': cumple,
        'num_palabras': palabras,
        'mensaje': mensaje
    }


def evaluar_estructura(stats):
    """El poema no requiere estructura de capítulos."""
    return {
        'cumple': True,
        'mensaje': 'El poema no requiere estructura de capítulos'
    }


def evaluar_legibilidad(stats):
    """Evalúa el índice de legibilidad. Mínimo recomendado: 30 (la poesía admite mayor complejidad)."""
    indice = stats.get('indice_legibilidad', 100)
    cumple = indice >= 30
    mensaje = f'Índice de legibilidad: {indice:.2f}. Mínimo recomendado: 30'
    return {
        'cumple': cumple,
        'indice': indice,
        'mensaje': mensaje
    }


def evaluar_poema(stats):
    """Evalúa todos los criterios y devuelve dict con resultados detallados."""
    return {
        'ortografia_gramatica': evaluar_ortografia_gramatica(stats),
        'longitud': evaluar_longitud(stats),
        'estructura': evaluar_estructura(stats),
        'legibilidad': evaluar_legibilidad(stats)
    }
