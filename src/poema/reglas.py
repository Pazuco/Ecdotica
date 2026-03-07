"""
Reglas específicas para el análisis y edición de poesía.
Editorial Nuevo Milenio
"""

import re
from collections import Counter


# Vocales para análisis métrico
VOCALES = 'aeiouáéíóúüAEIOUÁÉÍÓÚÜ'
VOCALES_LOWER = 'aeiouáéíóúü'

# Diptongos del español
DIPTONGOS = [
    'ai', 'au', 'ei', 'eu', 'ia', 'ie', 'io', 'iu',
    'oi', 'ou', 'ua', 'ue', 'ui', 'uo',
    'ái', 'áu', 'éi', 'éu', 'ía', 'íe', 'ío', 'íu',
    'ói', 'óu', 'úa', 'úe', 'úi', 'úo',
]

# Pares de antónimos comunes para detectar antítesis
PARES_ANTONIMOS = [
    ('vida', 'muerte'), ('amor', 'odio'), ('luz', 'sombra'),
    ('día', 'noche'), ('cielo', 'tierra'), ('bien', 'mal'),
    ('paz', 'guerra'), ('alegría', 'tristeza'), ('negro', 'blanco'),
    ('fuego', 'hielo'), ('silencio', 'ruido'), ('ausencia', 'presencia'),
]


def _contar_silabas_palabra(palabra):
    """Cuenta sílabas en una sola palabra mediante análisis vocálico con diptongos."""
    if not palabra:
        return 0

    palabra = palabra.lower()
    conteo = 0
    i = 0

    while i < len(palabra):
        if palabra[i] in VOCALES_LOWER:
            conteo += 1
            # Saltar diptongo si el siguiente carácter forma uno
            if i + 1 < len(palabra) and palabra[i:i + 2] in DIPTONGOS:
                i += 2
                continue
        i += 1

    return max(1, conteo)


def contar_silabas(verso):
    """
    Cuenta las sílabas métricas de un verso aplicando sinalefa entre palabras.

    La sinalefa une la última vocal de una palabra con la primera de la siguiente,
    reduciendo el cómputo en una sílaba por cada enlace encontrado.
    """
    verso = verso.strip().lower()
    if not verso:
        return 0

    verso_limpio = re.sub(r'[^\w\s]', '', verso)
    palabras = verso_limpio.split()
    if not palabras:
        return 0

    total = sum(_contar_silabas_palabra(p) for p in palabras)

    # Aplicar sinalefa entre palabras adyacentes
    for i in range(len(palabras) - 1):
        ultima = palabras[i][-1] if palabras[i] else ''
        primera = palabras[i + 1][0] if palabras[i + 1] else ''
        if ultima in VOCALES_LOWER and primera in VOCALES_LOWER:
            total -= 1

    return max(1, total)


def analizar_metrica(texto):
    """
    Analiza la métrica de cada verso y detecta si hay regularidad silábica.

    Devuelve el conteo de sílabas por verso, la métrica dominante y
    si al menos el 70% de los versos comparte esa métrica.
    """
    versos = [v for v in texto.strip().split('\n') if v.strip()]
    if not versos:
        return {
            'versos': [],
            'silabas_por_verso': [],
            'metrica_regular': False,
            'metrica_dominante': 0,
            'mensaje': 'No se encontraron versos',
        }

    resultado = [{'verso': v.strip(), 'silabas': contar_silabas(v)} for v in versos]
    conteos = [r['silabas'] for r in resultado]
    metrica_dominante = Counter(conteos).most_common(1)[0][0]
    regularidad = sum(1 for c in conteos if c == metrica_dominante) / len(conteos)

    return {
        'versos': resultado,
        'silabas_por_verso': conteos,
        'metrica_regular': regularidad >= 0.7,
        'metrica_dominante': metrica_dominante,
        'mensaje': (
            f'Métrica dominante: {metrica_dominante} sílabas '
            f'({regularidad * 100:.0f}% de versos)'
        ),
    }


def detectar_rima(texto):
    """
    Detecta el patrón de rima del poema: consonante, asonante o libre.

    Analiza las terminaciones de cada verso comparando consonantes y vocales
    en los últimos tres caracteres.
    """
    versos = [v.strip() for v in texto.strip().split('\n') if v.strip()]
    if len(versos) < 2:
        return {
            'tipo_rima': 'indeterminada',
            'terminaciones': [],
            'mensaje': 'Se necesitan al menos 2 versos para analizar la rima',
        }

    terminaciones = []
    for verso in versos:
        limpio = re.sub(r'[^\w]', '', verso).lower()
        terminaciones.append(limpio[-3:] if len(limpio) >= 3 else limpio)

    pares_consonante = 0
    pares_asonante = 0
    pares_totales = 0

    for i in range(len(terminaciones) - 1):
        for j in range(i + 1, min(i + 3, len(terminaciones))):
            t1, t2 = terminaciones[i], terminaciones[j]
            if t1 and t2:
                pares_totales += 1
                if t1 == t2:
                    pares_consonante += 1
                else:
                    vocales1 = ''.join(c for c in t1 if c in VOCALES_LOWER)
                    vocales2 = ''.join(c for c in t2 if c in VOCALES_LOWER)
                    if vocales1 and vocales1 == vocales2:
                        pares_asonante += 1

    if pares_totales == 0:
        tipo = 'libre'
    elif pares_consonante / pares_totales >= 0.4:
        tipo = 'consonante'
    elif (pares_consonante + pares_asonante) / pares_totales >= 0.4:
        tipo = 'asonante'
    else:
        tipo = 'libre'

    return {
        'tipo_rima': tipo,
        'terminaciones': terminaciones,
        'mensaje': f'Rima {tipo} detectada',
    }


def analizar_estrofas(texto):
    """
    Analiza la estructura estrófica: número de estrofas y versos por estrofa.

    Las estrofas se separan por líneas en blanco. Clasifica cada estrofa
    según su número de versos (dístico, terceto, cuarteto, etc.).
    """
    bloques = re.split(r'\n{2,}', texto.strip())
    estrofas = []

    nombres = {
        1: 'monostrofa', 2: 'dístico', 3: 'terceto',
        4: 'cuarteto', 5: 'quinteto', 6: 'sexteto',
        7: 'séptima', 8: 'octava', 10: 'décima',
    }

    for bloque in bloques:
        versos = [v for v in bloque.strip().split('\n') if v.strip()]
        if versos:
            n = len(versos)
            estrofas.append({
                'num_versos': n,
                'tipo': nombres.get(n, f'estrofa de {n} versos'),
            })

    estructura_regular = (
        len(set(e['num_versos'] for e in estrofas)) == 1
        if estrofas else False
    )

    return {
        'num_estrofas': len(estrofas),
        'estrofas': estrofas,
        'estructura_regular': estructura_regular,
        'mensaje': f'{len(estrofas)} estrofa(s) detectada(s)',
    }


def detectar_recursos_poeticos(texto):
    """
    Detecta recursos retóricos y poéticos: anáfora, aliteración y antítesis.

    - Anáfora: versos consecutivos que comienzan con la misma palabra.
    - Aliteración: verso con tres o más palabras que inician con el mismo fonema.
    - Antítesis: pares de palabras antónimas en el mismo verso.
    """
    versos = [v.strip() for v in texto.strip().split('\n') if v.strip()]
    recursos = {}

    # Anáfora
    anaforas = []
    for i in range(len(versos) - 1):
        p1 = versos[i].split()[0].lower() if versos[i].split() else ''
        p2 = versos[i + 1].split()[0].lower() if versos[i + 1].split() else ''
        if p1 and p1 == p2:
            anaforas.append(p1)

    recursos['anafora'] = {
        'detectada': bool(anaforas),
        'ejemplos': list(set(anaforas)),
        'mensaje': (
            f'Anáfora detectada en {len(anaforas)} par(es) de versos'
            if anaforas else 'Sin anáfora detectada'
        ),
    }

    # Aliteración
    aliteraciones = []
    for verso in versos:
        palabras = [p.lower() for p in re.findall(r'\b\w{3,}\b', verso)]
        if len(palabras) >= 2:
            iniciales = [p[0] for p in palabras]
            mas_comun = Counter(iniciales).most_common(1)
            if mas_comun and mas_comun[0][1] >= 3:
                aliteraciones.append(verso[:50])

    recursos['aliteracion'] = {
        'detectada': bool(aliteraciones),
        'ejemplos': aliteraciones[:3],
        'mensaje': (
            f'Aliteración detectada en {len(aliteraciones)} verso(s)'
            if aliteraciones else 'Sin aliteración detectada'
        ),
    }

    # Antítesis
    antitesis = []
    for verso in versos:
        verso_lower = verso.lower()
        for ant1, ant2 in PARES_ANTONIMOS:
            if ant1 in verso_lower and ant2 in verso_lower:
                antitesis.append(f'«{ant1}» / «{ant2}»')

    antitesis_unicos = list(set(antitesis))[:3]
    recursos['antitesis'] = {
        'detectada': bool(antitesis),
        'ejemplos': antitesis_unicos,
        'mensaje': (
            f'Antítesis detectada: {", ".join(antitesis_unicos)}'
            if antitesis else 'Sin antítesis detectada'
        ),
    }

    return recursos


class ReglaPoetaica:
    """Representa una regla de análisis poético aplicable a un texto."""

    def __init__(self, nombre, descripcion, funcion_validacion):
        """
        Inicializa la regla poética.

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
