"""
Pipeline central para evaluación editorial automatizada.
Editorial Nuevo Milenio
"""

import os
import sys

# Añadir src/ al path para importar módulos de reglas por género
_SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from criterios import novela, cuento, poema, ensayo, cronica
from utils import analizar_manuscrito

GENERO_CRITERIOS = {
    'novela': novela.evaluar_novela,
    'cuento': cuento.evaluar_cuento,
    'poema': poema.evaluar_poema,
    'ensayo': ensayo.evaluar_ensayo,
    'cronica': cronica.evaluar_cronica,
}

# Etiquetas legibles para el reporte cualitativo
_ETIQUETAS = {
    'metrica': 'Métrica',
    'rima': 'Rima',
    'estrofas': 'Estructura estrófica',
    'recursos': 'Recursos poéticos',
    'estructura': 'Estructura argumentativa',
    'conectores': 'Conectores lógicos',
    'referencias': 'Referencias bibliográficas',
    'tono': 'Tono',
    'temporalidad': 'Temporalidad',
    'fuentes': 'Fuentes y citas',
    'equilibrio': 'Equilibrio narrativo',
}

# Importar módulos de reglas con degradación suave
try:
    from poema import reglas as _reglas_poema
    from ensayo import reglas as _reglas_ensayo
    from cronica import reglas as _reglas_cronica

    def _analizar_poema(texto):
        return {
            'metrica': _reglas_poema.analizar_metrica(texto),
            'rima': _reglas_poema.detectar_rima(texto),
            'estrofas': _reglas_poema.analizar_estrofas(texto),
            'recursos': _reglas_poema.detectar_recursos_poeticos(texto),
        }

    def _analizar_ensayo(texto):
        return {
            'estructura': _reglas_ensayo.validar_estructura_argumentativa(texto),
            'conectores': _reglas_ensayo.detectar_conectores_logicos(texto),
            'referencias': _reglas_ensayo.detectar_referencias(texto),
            'tono': _reglas_ensayo.evaluar_tono_formal(texto),
        }

    def _analizar_cronica(texto):
        return {
            'temporalidad': _reglas_cronica.detectar_temporalidad(texto),
            'fuentes': _reglas_cronica.detectar_fuentes(texto),
            'equilibrio': _reglas_cronica.validar_equilibrio_narrativo(texto),
            'tono': _reglas_cronica.evaluar_tono_periodistico(texto),
        }

    GENERO_REGLAS = {
        'poema': _analizar_poema,
        'ensayo': _analizar_ensayo,
        'cronica': _analizar_cronica,
    }

except ImportError:
    GENERO_REGLAS = {}


def evaluar_manuscrito(stats, genero):
    """Evalúa un manuscrito según el género especificado."""
    if genero not in GENERO_CRITERIOS:
        raise ValueError(f'Género no implementado: {genero}')
    return GENERO_CRITERIOS[genero](stats)


def analizar_reglas_genero(texto, genero):
    """
    Aplica las reglas específicas del género al texto completo.

    Devuelve un dict con el análisis cualitativo, o None si el género
    no tiene reglas implementadas todavía.
    """
    if genero not in GENERO_REGLAS:
        return None
    return GENERO_REGLAS[genero](texto)


def reporte_resultados(resultados, genero):
    """Genera el reporte cuantitativo de evaluación (criterios de aptitud)."""
    mensajes = []
    for criterio, valor in resultados.items():
        cumple = valor.get('cumple', False)
        mensaje = valor.get('mensaje', f'{criterio}: sin información')
        estado = '✓' if cumple else '✗'
        mensajes.append(f'{estado} {mensaje}')
    apto = all(v.get('cumple', False) for v in resultados.values())
    mensajes.append('---')
    mensajes.append(
        f'APTO para publicación en {genero.upper()}'
        if apto
        else f'NO APTO para publicación en {genero.upper()}'
    )
    return '\n'.join(mensajes)


def reporte_analisis_cualitativo(analisis, genero):
    """
    Genera la sección cualitativa del reporte a partir del análisis de reglas.

    Formatea los resultados de los módulos de reglas específicas del género
    en texto legible para el editor.
    """
    if not analisis:
        return ''

    lineas = [f'\n--- Análisis cualitativo ({genero.upper()}) ---']

    for clave, resultado in analisis.items():
        etiqueta = _ETIQUETAS.get(clave, clave.capitalize())

        if not isinstance(resultado, dict):
            continue

        # Dict de dicts: recursos poéticos y similares (sin 'mensaje' en el nivel raíz)
        if all(isinstance(v, dict) for v in resultado.values()) and 'mensaje' not in resultado:
            lineas.append(f'  {etiqueta}:')
            for sub_resultado in resultado.values():
                if isinstance(sub_resultado, dict) and 'mensaje' in sub_resultado:
                    lineas.append(f'    · {sub_resultado["mensaje"]}')
        elif 'mensaje' in resultado:
            lineas.append(f'  {etiqueta}: {resultado["mensaje"]}')

    return '\n'.join(lineas)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Uso: python evaluador.py <ruta_manuscrito> <genero>')
        sys.exit(1)

    ruta = sys.argv[1]
    genero = sys.argv[2]

    with open(ruta, encoding='utf-8') as f:
        texto = f.read()

    stats = analizar_manuscrito(ruta)
    resultados = evaluar_manuscrito(stats, genero)
    print(reporte_resultados(resultados, genero))

    analisis = analizar_reglas_genero(texto, genero)
    if analisis:
        print(reporte_analisis_cualitativo(analisis, genero))
