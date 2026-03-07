"""
Reglas específicas para el análisis y edición de ensayos.
Editorial Nuevo Milenio
"""

import re


# Conectores lógicos clasificados por función discursiva
CONECTORES_LOGICOS = {
    'causales': [
        'porque', 'ya que', 'puesto que', 'dado que',
        'debido a', 'a causa de',
    ],
    'consecutivos': [
        'por tanto', 'por lo tanto', 'en consecuencia',
        'así pues', 'por ende', 'de modo que',
    ],
    'adversativos': [
        'sin embargo', 'no obstante', 'pero', 'aunque',
        'a pesar de', 'si bien',
    ],
    'aditivos': [
        'además', 'asimismo', 'igualmente', 'también',
        'del mismo modo', 'por otro lado',
    ],
    'conclusivos': [
        'en conclusión', 'en resumen', 'finalmente',
        'en definitiva', 'para concluir', 'en síntesis',
    ],
    'ejemplificativos': [
        'por ejemplo', 'es decir', 'esto es',
        'a saber', 'como ilustración', 'tal como',
    ],
}

# Patrones de referencias bibliográficas y citas
PATRONES_REFERENCIAS = [
    r'\([A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s[A-ZÁÉÍÓÚ][a-záéíóú]+)*,?\s*\d{4}\)',
    r'\([A-ZÁÉÍÓÚ][a-záéíóú]+\set\sal\.,?\s*\d{4}\)',
    r'según\s+[A-ZÁÉÍÓÚ][a-záéíóú]+',
    r'de acuerdo con\s+[A-ZÁÉÍÓÚ][a-záéíóú]+',
    r'citado en\s+[A-ZÁÉÍÓÚ][a-záéíóú]+',
    r'\[\d+\]',
]

# Palabras que marcan la tesis o propósito del ensayo
PALABRAS_TESIS = [
    'sostengo', 'argumento', 'planteo', 'propongo', 'demuestro',
    'considero', 'defiendo', 'afirmo', 'señalo', 'analizo',
    'el objetivo', 'el propósito', 'en este ensayo',
    'el presente trabajo', 'a lo largo de', 'me propongo',
]

# Palabras que marcan la conclusión del ensayo
PALABRAS_CONCLUSION = [
    'en conclusión', 'en resumen', 'para concluir', 'finalmente',
    'en definitiva', 'en síntesis', 'a modo de cierre',
    'como resultado', 'se puede concluir', 'queda demostrado',
    'hemos visto que',
]

# Marcadores de registro informal
MARCADORES_INFORMALES = [
    'bueno', 'o sea', 'a ver', 'la verdad', 'la neta',
    'súper', 'genial', 'increíble', 'jaja', 'xd',
    'que tal', 'oye,', 'mira,', 'fíjate', 'imagínate',
]


def detectar_conectores_logicos(texto):
    """
    Detecta y clasifica los conectores lógicos presentes en el ensayo.

    Devuelve la frecuencia por tipo y evalúa si hay diversidad suficiente
    (se consideran necesarios al menos 3 tipos distintos).
    """
    texto_lower = texto.lower()
    resultado = {}
    total_encontrados = 0

    for tipo, conectores in CONECTORES_LOGICOS.items():
        encontrados = []
        for conector in conectores:
            n = len(re.findall(r'\b' + re.escape(conector) + r'\b', texto_lower))
            if n > 0:
                encontrados.append({'conector': conector, 'ocurrencias': n})
        subtotal = sum(c['ocurrencias'] for c in encontrados)
        resultado[tipo] = {'encontrados': encontrados, 'total': subtotal}
        total_encontrados += subtotal

    tipos_usados = [t for t, v in resultado.items() if v['total'] > 0]

    return {
        'conectores_por_tipo': resultado,
        'total_conectores': total_encontrados,
        'tipos_usados': tipos_usados,
        'diversidad_adecuada': len(tipos_usados) >= 3,
        'mensaje': (
            f'{total_encontrados} conectores lógicos de '
            f'{len(tipos_usados)} tipo(s) distintos'
        ),
    }


def detectar_referencias(texto):
    """
    Detecta el uso de referencias, citas y fuentes en el ensayo.

    Analiza patrones como (Autor, año), según Autor, [N] y similares.
    """
    referencias = []
    for patron in PATRONES_REFERENCIAS:
        referencias.extend(re.findall(patron, texto))

    # Eliminar duplicados preservando orden
    vistas = set()
    unicas = []
    for r in referencias:
        if r not in vistas:
            vistas.add(r)
            unicas.append(r)

    return {
        'num_referencias': len(referencias),
        'referencias_unicas': unicas[:10],
        'usa_referencias': bool(referencias),
        'mensaje': (
            f'{len(referencias)} referencia(s) detectada(s)'
            if referencias else 'Sin referencias detectadas'
        ),
    }


def validar_estructura_argumentativa(texto):
    """
    Valida que el ensayo tenga una estructura argumentativa básica:
    tesis (introducción), desarrollo y conclusión.

    La tesis se busca en el primer 25% de párrafos; la conclusión
    en el último párrafo; el desarrollo en el cuerpo intermedio.
    """
    parrafos = [p.strip() for p in re.split(r'\n{2,}', texto) if p.strip()]
    if not parrafos:
        return {
            'tiene_tesis': False,
            'tiene_desarrollo': False,
            'tiene_conclusion': False,
            'estructura_completa': False,
            'mensaje': 'No se pudo analizar la estructura: texto vacío',
        }

    limite = max(1, len(parrafos) // 4)
    inicio = ' '.join(parrafos[:limite]).lower()
    tiene_tesis = any(p in inicio for p in PALABRAS_TESIS)

    parrafos_medios = parrafos[limite:-1] if len(parrafos) > 2 else parrafos[1:]
    conectores_desarrollo = sum(
        1
        for p in parrafos_medios
        for conectores in CONECTORES_LOGICOS.values()
        for c in conectores
        if c in p.lower()
    )
    tiene_desarrollo = len(parrafos_medios) >= 2 and conectores_desarrollo >= 1

    ultimo = parrafos[-1].lower() if parrafos else ''
    tiene_conclusion = any(p in ultimo for p in PALABRAS_CONCLUSION)

    partes = []
    if tiene_tesis:
        partes.append('tesis')
    if tiene_desarrollo:
        partes.append('desarrollo')
    if tiene_conclusion:
        partes.append('conclusión')

    return {
        'tiene_tesis': tiene_tesis,
        'tiene_desarrollo': tiene_desarrollo,
        'tiene_conclusion': tiene_conclusion,
        'estructura_completa': tiene_tesis and tiene_desarrollo and tiene_conclusion,
        'mensaje': (
            f'Estructura detectada: {", ".join(partes)}'
            if partes else 'Estructura argumentativa incompleta'
        ),
    }


def evaluar_tono_formal(texto):
    """
    Evalúa si el ensayo mantiene un tono formal y académico.

    Detecta informalismos y un uso excesivo de la primera persona
    (más del 30% de las oraciones).
    """
    texto_lower = texto.lower()
    informalismos = [m for m in MARCADORES_INFORMALES if m in texto_lower]

    oraciones = re.split(r'[.!?]+', texto)
    oraciones_1p = sum(
        1 for o in oraciones
        if re.search(r'\b(yo |me |mi |mis |mí)\b', o.lower())
    )
    ratio_1p = oraciones_1p / max(1, len(oraciones))

    return {
        'tono_formal': not informalismos and ratio_1p < 0.3,
        'informalismos_detectados': informalismos[:5],
        'ratio_primera_persona': round(ratio_1p, 2),
        'mensaje': (
            'Tono formal adecuado'
            if not informalismos
            else f'Informalismos detectados: {", ".join(informalismos[:3])}'
        ),
    }


class ReglaEnsayistica:
    """Representa una regla de análisis ensayístico aplicable a un texto."""

    def __init__(self, nombre, descripcion, funcion_validacion):
        """
        Inicializa la regla ensayística.

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
