"""
Módulo de criterios editoriales para ensayo.
Editorial Nuevo Milenio
"""


def evaluar_ortografia_gramatica(stats):
    """Evalúa ortografía y gramática. Se espera menos de 3 errores graves por cada 10,000 palabras."""
    errores_graves = stats.get('errores_graves', 0)
    palabras = stats.get('num_palabras', 1)
    tasa_error = errores_graves / palabras * 10000
    return {
        'cumple': tasa_error < 3,
        'tasa_error': tasa_error,
        'mensaje': f'Tasa de errores: {tasa_error:.2f} por 10,000 palabras'
    }


def evaluar_longitud(stats):
    """Evalúa el rango de palabras del ensayo. Entre 1,500 y 30,000 palabras."""
    palabras = stats.get('num_palabras', 0)
    cumple = 1500 <= palabras <= 30000
    if palabras < 1500:
        mensaje = f'El ensayo tiene {palabras} palabras. Mínimo requerido: 1,500'
    elif palabras > 30000:
        mensaje = f'El ensayo tiene {palabras} palabras. Máximo recomendado: 30,000'
    else:
        mensaje = f'Longitud adecuada: {palabras} palabras'
    return {
        'cumple': cumple,
        'num_palabras': palabras,
        'mensaje': mensaje
    }


def evaluar_estructura(stats):
    """El ensayo puede presentarse como texto continuo sin capítulos."""
    return {
        'cumple': True,
        'mensaje': 'El ensayo no requiere estructura de capítulos'
    }


def evaluar_legibilidad(stats):
    """Evalúa el índice de legibilidad. Mínimo recomendado: 40 (textos académicos admiten mayor densidad)."""
    indice = stats.get('indice_legibilidad', 100)
    cumple = indice >= 40
    mensaje = f'Índice de legibilidad: {indice:.2f}. Mínimo recomendado: 40'
    return {
        'cumple': cumple,
        'indice': indice,
        'mensaje': mensaje
    }


def evaluar_ensayo(stats):
    """Evalúa todos los criterios y devuelve dict con resultados detallados."""
    return {
        'ortografia_gramatica': evaluar_ortografia_gramatica(stats),
        'longitud': evaluar_longitud(stats),
        'estructura': evaluar_estructura(stats),
        'legibilidad': evaluar_legibilidad(stats)
    }
