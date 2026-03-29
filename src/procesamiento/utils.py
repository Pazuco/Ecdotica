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
    """Calcula el índice de legibilidad para español usando textstat (Flesch Reading Ease).

    Requiere: pip install textstat
    Si textstat no está instalado, usa fórmula de respaldo basada en Flesch-Kincaid.
    Retorna un valor entre 0 y 100.
    """
    if not texto or not texto.strip():
        return 100
    try:
        import textstat
        textstat.set_lang("es")
        resultado = textstat.flesch_reading_ease(texto)
        return max(0, min(100, resultado))
    except ImportError:
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


def generar_sinopsis(texto, num_oraciones=3):
    """Genera una sinopsis automática del texto usando sumy (algoritmo LSA).

    Requiere: pip install sumy numpy
    Si sumy no está instalado, retorna las primeras num_oraciones del texto como fallback.
    Retorna cadena vacía si el texto está vacío.
    """
    if not texto or not texto.strip():
        return ""
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer
        parser = PlaintextParser.from_string(texto, Tokenizer('spanish'))
        resumidor = LsaSummarizer()
        oraciones = resumidor(parser.document, num_oraciones)
        return ' '.join(str(o) for o in oraciones)
    except ImportError:
        import re
        oraciones = re.split(r'(?<=[.!?])\s+', texto.strip())
        return ' '.join(oraciones[:num_oraciones])


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
            dep = "pypdf" if ext == '.pdf' else "python-docx"
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
