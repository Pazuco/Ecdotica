import os

# Para PDF: instalar 'PyPDF2'
# Para DOCX: instalar 'python-docx'
# Para TXT: estándar
# Estructura para futura integración con SpaCy y LanguageTool comentada

class ProcesadorDeArchivos:
    """
    Clase para procesar archivos PDF, TXT y DOCX.
    Uso:
    - PDF: pip install PyPDF2
    - DOCX: pip install python-docx
    - SpaCy: pip install spacy
    - LanguageTool: pip install language-tool-python
    """
    
    def extraer_texto(self, ruta):
        ext = os.path.splitext(ruta)[1].lower()
        if ext == '.pdf':
            return self._extraer_pdf(ruta)
        elif ext == '.docx':
            return self._extraer_docx(ruta)
        elif ext == '.txt':
            return self._extraer_txt(ruta)
        else:
            raise ValueError("Tipo de archivo no soportado")
    
    def _extraer_pdf(self, ruta):
        # Requiere PyPDF2
        texto = ""
        try:
            import PyPDF2
            with open(ruta, 'rb') as f:
                lector = PyPDF2.PdfReader(f)
                for pagina in lector.pages:
                    texto += pagina.extract_text() or ""
        except ImportError:
            texto = "PyPDF2 no instalado"
        return texto
    
    def _extraer_docx(self, ruta):
        # Requiere python-docx
        texto = ""
        try:
            import docx
            doc = docx.Document(ruta)
            for parrafo in doc.paragraphs:
                texto += parrafo.text + "\n"
        except ImportError:
            texto = "python-docx no instalado"
        return texto
    
    def _extraer_txt(self, ruta):
        # TXT estándar
        with open(ruta, encoding="utf-8") as f:
            return f.read()
    
    # Ejemplo de cómo integrar SpaCy en el futuro:
    # def analizar_con_spacy(self, texto):
    #     import spacy
    #     nlp = spacy.load("es_core_news_sm")
    #     doc = nlp(texto)
    #     return doc
    
    # Ejemplo de cómo integrar LanguageTool:
    # def corregir_con_languagetool(self, texto):
    #     import language_tool_python
    #     tool = language_tool_python.LanguageTool('es')
    #     matches = tool.check(texto)
    #     return tool.correct(texto)


# ============================================================================
# FUNCIONES DE EJEMPLO PARA ANÁLISIS DE TEXTOS CON SPACY Y LANGUAGETOOL
# ============================================================================
# Las siguientes funciones demuestran cómo utilizar SpaCy y LanguageTool
# para analizar el texto de muestra 'Amor sin libertad' de Yuri Ortuño,
# siguiendo los ejemplos incluidos en CONTRIBUTING.md

import spacy
import language_tool_python


def analizar_texto_ejemplo():
    """
    Función de ejemplo que analiza el texto 'Amor sin libertad' de Yuri Ortuño
    utilizando SpaCy para análisis morfosintáctico y LanguageTool para corrección.
    
    Esta función demuestra las capacidades de procesamiento de textos literarios
    que se pueden aplicar en el proyecto Ecdotica.
    """
    
    # Cargar el modelo de SpaCy para español
    # Nota: Requiere instalar el modelo con: python -m spacy download es_core_news_sm
    print("Cargando modelo de SpaCy para español...")
    nlp = spacy.load("es_core_news_sm")
    
    # Inicializar LanguageTool para español
    print("Inicializando LanguageTool...")
    tool = language_tool_python.LanguageTool('es')
    
    # Leer el archivo de muestra
    ruta_sample = os.path.join(os.path.dirname(__file__), '..', 'samples', 'sample.txt')
    print(f"Leyendo archivo: {ruta_sample}")
    
    try:
        with open(ruta_sample, 'r', encoding='utf-8') as f:
            texto = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_sample}")
        return
    
    # Tomar solo los primeros párrafos para el análisis de ejemplo
    # (procesar todo el texto puede ser muy largo para una demostración)
    primer_parrafo = texto.split('\n\n')[1] if '\n\n' in texto else texto[:500]
    
    print("\n" + "="*70)
    print("ANÁLISIS CON SPACY")
    print("="*70)
    
    # Procesar el texto con SpaCy
    doc = nlp(primer_parrafo)
    
    # Ejemplo 1: Análisis de entidades nombradas
    print("\n1. ENTIDADES NOMBRADAS:")
    print("-" * 50)
    if doc.ents:
        for ent in doc.ents:
            print(f"  - {ent.text:20} | Tipo: {ent.label_:10} | {spacy.explain(ent.label_)}")
    else:
        print("  No se encontraron entidades nombradas en este fragmento.")
    
    # Ejemplo 2: Análisis de tokens (primeros 10)
    print("\n2. ANÁLISIS DE TOKENS (primeros 10):")
    print("-" * 50)
    print(f"  {'Token':15} | {'Lema':15} | {'POS':8} | {'Tag':8} | {'Dep':10}")
    print("-" * 50)
    for token in list(doc)[:10]:
        print(f"  {token.text:15} | {token.lemma_:15} | {token.pos_:8} | {token.tag_:8} | {token.dep_:10}")
    
    # Ejemplo 3: Análisis de oraciones
    print("\n3. SEGMENTACIÓN DE ORACIONES:")
    print("-" * 50)
    oraciones = list(doc.sents)
    print(f"  Total de oraciones encontradas: {len(oraciones)}")
    if len(oraciones) > 0:
        print(f"\n  Primera oración: {oraciones[0].text[:100]}...")
    
    # Ejemplo 4: Análisis de sustantivos y verbos
    print("\n4. SUSTANTIVOS Y VERBOS PRINCIPALES:")
    print("-" * 50)
    sustantivos = [token.text for token in doc if token.pos_ == "NOUN"]
    verbos = [token.text for token in doc if token.pos_ == "VERB"]
    print(f"  Sustantivos encontrados ({len(sustantivos)}): {', '.join(sustantivos[:10])}...")
    print(f"  Verbos encontrados ({len(verbos)}): {', '.join(verbos[:10])}...")
    
    print("\n" + "="*70)
    print("ANÁLISIS CON LANGUAGETOOL")
    print("="*70)
    
    # Analizar un fragmento más pequeño con LanguageTool
    # (tomar solo las primeras 2-3 oraciones para evitar análisis muy largos)
    fragmento_lt = '. '.join(primer_parrafo.split('.')[:3]) + '.'
    
    # Obtener sugerencias de corrección
    matches = tool.check(fragmento_lt)
    
    print(f"\n5. SUGERENCIAS DE CORRECCIÓN:")
    print("-" * 50)
    if matches:
        print(f"  Se encontraron {len(matches)} posibles mejoras:\n")
        for i, match in enumerate(matches[:5], 1):  # Mostrar solo las primeras 5
            print(f"  {i}. Posición {match.offset}-{match.offset + match.errorLength}")
            print(f"     Contexto: ...{match.context}...")
            print(f"     Mensaje: {match.message}")
            if match.replacements:
                print(f"     Sugerencias: {', '.join(match.replacements[:3])}")
            print()
    else:
        print("  ¡Excelente! No se encontraron sugerencias de corrección.")
    
    # Cerrar LanguageTool
    tool.close()
    
    print("\n" + "="*70)
    print("ANÁLISIS COMPLETADO")
    print("="*70)
    print("\nEste es un ejemplo básico de las capacidades de análisis.")
    print("Para análisis más detallados, consulta la documentación en CONTRIBUTING.md")
    print()


def obtener_estadisticas_texto(ruta_archivo):
    """
    Obtiene estadísticas básicas de un archivo de texto.
    
    Args:
        ruta_archivo (str): Ruta al archivo de texto
    
    Returns:
        dict: Diccionario con estadísticas del texto
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            texto = f.read()
        
        # Cargar modelo de SpaCy
        nlp = spacy.load("es_core_news_sm")
        doc = nlp(texto)
        
        estadisticas = {
            'caracteres': len(texto),
            'palabras': len([token for token in doc if not token.is_space]),
            'oraciones': len(list(doc.sents)),
            'tokens': len(doc),
            'entidades': len(doc.ents)
        }
        
        return estadisticas
    
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return None


if __name__ == "__main__":
    """
    Bloque principal que ejecuta la función de ejemplo cuando se ejecuta el script directamente.
    
    Uso:
        python src/procesamiento/archivos.py
    """
    print("\n" + "#"*70)
    print("#  EJEMPLO DE ANÁLISIS DE TEXTO CON SPACY Y LANGUAGETOOL")
    print("#  Proyecto: Ecdotica")
    print("#  Texto de muestra: 'Amor sin libertad' por Yuri Ortuño León")
    print("#"*70 + "\n")
    
    # Ejecutar análisis de ejemplo
    analizar_texto_ejemplo()
    
    # Mostrar estadísticas básicas
    print("\n" + "="*70)
    print("ESTADÍSTICAS DEL TEXTO COMPLETO")
    print("="*70)
    
    ruta_sample = os.path.join(os.path.dirname(__file__), '..', 'samples', 'sample.txt')
    stats = obtener_estadisticas_texto(ruta_sample)
    
    if stats:
        print(f"\n  Caracteres totales: {stats['caracteres']:,}")
        print(f"  Palabras totales: {stats['palabras']:,}")
        print(f"  Oraciones totales: {stats['oraciones']:,}")
        print(f"  Tokens totales: {stats['tokens']:,}")
        print(f"  Entidades nombradas: {stats['entidades']}")
        print()
