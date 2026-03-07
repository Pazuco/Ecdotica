"""
Reglas específicas para el análisis y edición de crónicas.
Editorial Nuevo Milenio
"""

import re


# Marcadores temporales que estructuran la narrativa cronística
MARCADORES_TEMPORALES = {
    'pasado': [
        'ayer', 'anteayer', 'el año pasado', 'hace años', 'hace décadas',
        'en aquel entonces', 'en ese momento', 'en aquella época',
        'años atrás', 'tiempo atrás', 'anteriormente',
    ],
    'presente': [
        'hoy', 'actualmente', 'en la actualidad', 'hoy en día', 'ahora',
        'en este momento', 'a día de hoy',
    ],
    'progresion': [
        'primero', 'luego', 'después', 'más tarde', 'finalmente',
        'mientras tanto', 'al mismo tiempo', 'días después',
        'semanas más tarde', 'entonces', 'a continuación', 'posteriormente',
    ],
}

# Verbos de atribución periodística
VERBOS_ATRIBUCION = [
    'dijo', 'afirmó', 'señaló', 'explicó', 'declaró', 'indicó',
    'comentó', 'aseguró', 'reveló', 'contó', 'manifestó', 'expresó',
    'relató', 'narró', 'describió', 'detalló', 'reconoció', 'admitió',
]

# Marcadores de registro subjetivo (voz del cronista)
PATRONES_PRIMERA_PERSONA = [
    r'\byo\b', r'\bme\b', r'\bmi\b', r'\bmis\b',
    r'\bnosotros\b', r'\bnosotras\b', r'\bnos\b', r'\bnuestro\b',
    r'\bestuve\b', r'\bfui\b', r'\bvi\b', r'\bpresencié\b',
    r'\brecuerdo\b', r'\bsentí\b', r'\bpensé\b',
]

# Marcadores de objetividad periodística
MARCADORES_OBJETIVOS = [
    'según', 'de acuerdo con', 'conforme a', 'reportes indican',
    'datos muestran', 'estadísticas', 'cifras', 'registros',
    'fuentes', 'testimonios', 'documentos',
]


def detectar_temporalidad(texto):
    """
    Detecta y analiza los marcadores temporales en la crónica.

    Clasifica los marcadores en pasado, presente y progresión narrativa,
    y evalúa si hay una progresión cronológica clara.
    """
    texto_lower = texto.lower()
    encontrados_por_tipo = {}
    total = 0

    for tipo, marcadores in MARCADORES_TEMPORALES.items():
        encontrados = []
        for marcador in marcadores:
            n = len(re.findall(r'\b' + re.escape(marcador) + r'\b', texto_lower))
            if n > 0:
                encontrados.append({'marcador': marcador, 'ocurrencias': n})
        encontrados_por_tipo[tipo] = encontrados
        total += sum(m['ocurrencias'] for m in encontrados)

    tiene_pasado = bool(encontrados_por_tipo.get('pasado'))
    tiene_presente = bool(encontrados_por_tipo.get('presente'))
    tiene_progresion = bool(encontrados_por_tipo.get('progresion'))

    return {
        'marcadores_por_tipo': encontrados_por_tipo,
        'total_marcadores': total,
        'tiene_pasado': tiene_pasado,
        'tiene_presente': tiene_presente,
        'tiene_progresion': tiene_progresion,
        'progresion_temporal': tiene_pasado or tiene_presente or tiene_progresion,
        'mensaje': f'{total} marcador(es) temporal(es) detectado(s)',
    }


def detectar_fuentes(texto):
    """
    Detecta el uso de fuentes, testimonios y citas directas en la crónica.

    Analiza citas entre comillas, verbos de atribución periodística
    y marcadores de información objetiva.
    """
    # Citas directas entre comillas tipográficas o normales (mín. 10 caracteres)
    citas = re.findall(r'[«""][^»""]{10,}[»""]', texto)

    texto_lower = texto.lower()
    verbos_encontrados = []
    for verbo in VERBOS_ATRIBUCION:
        n = len(re.findall(r'\b' + re.escape(verbo) + r'\b', texto_lower))
        if n > 0:
            verbos_encontrados.append({'verbo': verbo, 'ocurrencias': n})

    objetivos_encontrados = [m for m in MARCADORES_OBJETIVOS if m in texto_lower]
    total_atribuciones = sum(v['ocurrencias'] for v in verbos_encontrados)

    return {
        'citas_directas': len(citas),
        'ejemplos_citas': [c[:60] + '…' for c in citas[:3]],
        'verbos_atribucion': verbos_encontrados,
        'total_atribuciones': total_atribuciones,
        'marcadores_objetivos': objetivos_encontrados,
        'usa_fuentes': bool(citas) or total_atribuciones > 0,
        'mensaje': (
            f'{len(citas)} cita(s) directa(s) y '
            f'{total_atribuciones} atribución(es) detectada(s)'
        ),
    }


def validar_equilibrio_narrativo(texto):
    """
    Valida el equilibrio entre la narración subjetiva (voz del cronista)
    y los hechos objetivos (datos, fuentes, testimonios).

    Una crónica equilibrada no debe superar el 70% en ninguna de las dos
    perspectivas respecto al total de oraciones.
    """
    oraciones = [o.strip() for o in re.split(r'[.!?]+', texto) if o.strip()]
    if not oraciones:
        return {
            'ratio_subjetivo': 0.0,
            'ratio_objetivo': 0.0,
            'equilibrio': False,
            'mensaje': 'No se pudo analizar: texto vacío',
        }

    oraciones_subjetivas = sum(
        1 for o in oraciones
        if any(re.search(patron, o.lower()) for patron in PATRONES_PRIMERA_PERSONA)
    )
    oraciones_objetivas = sum(
        1 for o in oraciones
        if any(
            marcador in o.lower()
            for marcador in MARCADORES_OBJETIVOS + VERBOS_ATRIBUCION
        )
    )

    total = len(oraciones)
    ratio_subjetivo = oraciones_subjetivas / total
    ratio_objetivo = oraciones_objetivas / total
    equilibrio = ratio_subjetivo <= 0.7 and ratio_objetivo <= 0.7

    if ratio_subjetivo > 0.7:
        diagnostico = 'Predomina la voz personal; añadir más datos y fuentes'
    elif ratio_objetivo > 0.7:
        diagnostico = 'Predomina el registro informativo; añadir más voz narrativa del cronista'
    else:
        diagnostico = 'Equilibrio narrativo adecuado entre voz personal y datos objetivos'

    return {
        'ratio_subjetivo': round(ratio_subjetivo, 2),
        'ratio_objetivo': round(ratio_objetivo, 2),
        'oraciones_subjetivas': oraciones_subjetivas,
        'oraciones_objetivas': oraciones_objetivas,
        'equilibrio': equilibrio,
        'mensaje': diagnostico,
    }


def evaluar_tono_periodistico(texto):
    """
    Evalúa si la crónica mantiene el tono periodístico-narrativo del género.

    Combina los análisis de temporalidad, fuentes y equilibrio narrativo.
    Se considera adecuado si al menos 2 de los 3 criterios se cumplen.
    """
    temporalidad = detectar_temporalidad(texto)
    fuentes = detectar_fuentes(texto)
    equilibrio = validar_equilibrio_narrativo(texto)

    criterios = {
        'tiene_temporalidad': temporalidad['progresion_temporal'],
        'usa_fuentes': fuentes['usa_fuentes'],
        'equilibrio_narrativo': equilibrio['equilibrio'],
    }
    puntuacion = sum(criterios.values())

    return {
        'criterios': criterios,
        'puntuacion': puntuacion,
        'tono_adecuado': puntuacion >= 2,
        'mensaje': (
            'Tono periodístico-narrativo adecuado'
            if puntuacion >= 2
            else (
                f'Faltan elementos clave: '
                f'{[k for k, v in criterios.items() if not v]}'
            )
        ),
    }


class ReglaCronistica:
    """Representa una regla de análisis cronístico aplicable a un texto."""

    def __init__(self, nombre, descripcion, funcion_validacion):
        """
        Inicializa la regla cronística.

        :param nombre: Nombre identificador de la regla.
        :param descripcion: Descripción breve de qué evalúa.
        :param funcion_validacion: Función que recibe el texto y devuelve un dict.
        """
        self.nombre = nombre
        self.descripcion = descripcion
        self.funcion_validacion = funcion_validacion

    def aplicar(self, texto):
        """Aplica la regla al texto y devuelve el resultado de la validación."""
        return self.funcion_validacion(texto)
