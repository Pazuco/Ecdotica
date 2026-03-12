"""Prompts para la generación de Informes de Lectura con GPT-4.

Contiene los prompts del sistema y del usuario para generar informes
de lectura profesionales en español con calidad de crítica literaria.
"""

from api.models.reading_reports import FormatoInforme

LONGITUDES_FORMATO = {
    FormatoInforme.BREVE: "aproximadamente 500 palabras en total",
    FormatoInforme.ESTANDAR: "aproximadamente 1500 palabras en total",
    FormatoInforme.DETALLADO: "3000 palabras o más en total",
}

INSTRUCCIONES_FORMATO = {
    FormatoInforme.BREVE: (
        "Sé conciso y directo. Cada sección debe tener 2-3 oraciones. "
        "Prioriza la sinopsis y la valoración crítica."
    ),
    FormatoInforme.ESTANDAR: (
        "Desarrolla cada sección con párrafos completos. "
        "Incluye ejemplos y observaciones específicas cuando sea posible."
    ),
    FormatoInforme.DETALLADO: (
        "Elabora un análisis exhaustivo y académico de cada sección. "
        "Incluye comparaciones con otras obras, citas relevantes si las conoces, "
        "análisis de técnicas narrativas específicas, y contexto histórico-literario amplio. "
        "Cada sección debe ser un ensayo breve en sí mismo."
    ),
}

PROMPT_SISTEMA = """Eres un crítico literario profesional y académico hispanohablante \
con amplia experiencia en literatura latinoamericana y universal. \
Tu especialidad es elaborar informes de lectura (reseñas críticas) \
de alta calidad para editoriales, autores y lectores exigentes.

Directrices:
- Escribe siempre en español con registro formal pero accesible.
- Basa tu análisis en tu conocimiento de la obra. Si no conoces el libro, \
  genera un análisis plausible basado en el título, autor y género proporcionados, \
  indicando que el análisis se basa en información disponible.
- NO incluyas spoilers importantes en la sinopsis.
- Sé honesto en tu valoración crítica — señala tanto fortalezas como debilidades.
- Fundamenta tus opiniones con argumentos literarios sólidos.
- Adapta la profundidad del análisis al formato solicitado.

Responde EXCLUSIVAMENTE con un objeto JSON válido con la siguiente estructura exacta:
{
    "ficha_bibliografica": {
        "titulo": "string",
        "autor": "string",
        "genero": "string o null",
        "anio_publicacion": "string o null",
        "editorial": "string o null",
        "idioma": "string",
        "paginas_estimadas": "string o null"
    },
    "sinopsis": "string",
    "analisis_tematico": "string",
    "analisis_estilo_estructura": "string",
    "contexto_literario": "string",
    "valoracion_critica": "string",
    "publico_recomendado": "string",
    "calificacion": numero_entero_1_a_5,
    "justificacion_calificacion": "string"
}

NO incluyas texto fuera del JSON. NO uses bloques de código markdown. \
Responde SOLO con el JSON."""

PLANTILLA_USUARIO = """Genera un informe de lectura profesional para el siguiente libro:

**Título:** {titulo}
**Autor:** {autor}
**Género:** {genero}
{notas_seccion}

**Formato solicitado:** {formato} ({longitud})

**Instrucciones de formato:** {instrucciones_formato}

Genera el informe de lectura completo en formato JSON siguiendo la estructura indicada."""


def construir_prompt_informe(
    titulo: str,
    autor: str,
    genero: str | None = None,
    notas_usuario: str | None = None,
    formato: FormatoInforme = FormatoInforme.ESTANDAR,
) -> tuple[str, str]:
    """Construye los prompts del sistema y del usuario para generar un informe.

    Args:
        titulo: Título del libro.
        autor: Nombre del autor.
        genero: Género literario (opcional).
        notas_usuario: Notas o áreas de enfoque del usuario (opcional).
        formato: Formato del informe (breve, estándar, detallado).

    Returns:
        Tupla con (prompt_sistema, prompt_usuario).
    """
    genero_texto = genero if genero else "No especificado"

    notas_seccion = ""
    if notas_usuario:
        notas_seccion = f"**Notas del usuario / Áreas de enfoque:** {notas_usuario}"

    longitud = LONGITUDES_FORMATO[formato]
    instrucciones = INSTRUCCIONES_FORMATO[formato]

    prompt_usuario = PLANTILLA_USUARIO.format(
        titulo=titulo,
        autor=autor,
        genero=genero_texto,
        notas_seccion=notas_seccion,
        formato=formato.value,
        longitud=longitud,
        instrucciones_formato=instrucciones,
    )

    return PROMPT_SISTEMA, prompt_usuario
