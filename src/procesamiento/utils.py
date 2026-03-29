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
    """Detecta errores ortográficos y gramaticales usando LanguageTool.

    Requiere: pip install language-tool-python
    Si LanguageTool no está instalado, devuelve 0 y no bloquea la evaluación.
    """
    try:
        import language_tool_python
        tool = language_tool_python.LanguageTool('es')
        matches = tool.check(texto)
        tool.close()
        return len(matches)
    except ImportError:
        return 0


def analizar_manuscrito(path):
    """Lee un archivo .txt, .pdf o .docx y extrae estadísticas de análisis."""
    import os
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    ext = os.path.splitext(path)[1].lower()
    formatos_validos = ['.txt', '.pdf', '.docx']

    if ext == '.txt':
        with open(path, encoding='utf-8') as f:
            texto = f.read()
    elif ext in ('.pdf', '.docx'):
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from archivos import ProcesadorDeArchivos
        texto = ProcesadorDeArchivos().extraer_texto(path)
        if texto in ("PyPDF2 no instalado", "python-docx no instalado"):
            dep = "PyPDF2" if ext == '.pdf' else "python-docx"
            raise ImportError(
                f"Dependencia faltante para archivos {ext}: ejecuta 'pip install {dep}'"
            )
        if not texto.strip():
            raise ValueError(
                f"No se pudo extraer texto del archivo '{path}'. "
                "Verifique que el archivo contiene texto seleccionable."
            )
    else:
        raise ValueError(
            f"Formato '{ext}' no soportado. "
            f"Formatos válidos: {', '.join(formatos_validos)}"
        )

    stats = {
        'num_palabras': contar_palabras(texto),
        'num_capitulos': contar_capitulos(texto),
        'indice_legibilidad': calcular_legibilidad(texto),
        'errores_graves': detectar_errores(texto),
    }
    return stats
