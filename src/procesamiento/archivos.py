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
